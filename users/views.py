import os
import requests
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from .serializers import RegisterSerializer
from .models import CustomUser
from .supabase_client import supabase
from .serializers import UserSearchSerializer

User = get_user_model()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# ----------------------------
# REGISTER USER
# ----------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(
                {"message": "User registered successfully. Check your email to verify account."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------
# VERIFY SUPABASE USER EMAIL
# ----------------------------
class VerifySupabaseUserView(generics.GenericAPIView):
    def get(self, request):
        access_token = request.GET.get("access_token")
        if not access_token:
            return Response({"error": "Access token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_info = supabase.auth.get_user(access_token)
            supabase_user = getattr(user_info, "user", None)
        except Exception as e:
            return Response({"error": f"Failed to fetch user from Supabase: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not supabase_user:
            return Response({"error": "Invalid Supabase user"}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(email=supabase_user.email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if getattr(supabase_user, "confirmed_at", None):
            user.is_active = True
            user.save()
            return Response({"message": "User verified successfully"}, status=status.HTTP_200_OK)

        return Response({"message": "User not verified yet"}, status=status.HTTP_200_OK)


# ----------------------------
# LOGIN USER
# ----------------------------
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")

        if not password or (not email and not username):
            return Response({"error": "Username/Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get user object
        try:
            if email:
                user_obj = User.objects.get(email=email)
            else:
                user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Authenticate Django user
        user = authenticate(request, username=user_obj.get_username(), password=password)
        if not user or not user.is_active:
            return Response({"error": "Invalid credentials or user not active"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate Django JWT tokens
        refresh = RefreshToken.for_user(user)

        # Supabase login
        access_token = None
        try:
            supabase_response = supabase.auth.sign_in_with_password({"email": user.email, "password": password})
            # supabase_response can be dict/obj depending on client; handle safely
            if supabase_response and getattr(supabase_response, "session", None):
                access_token = supabase_response.session.access_token
        except Exception as e:
            # don't block login if supabase sign-in fails; log for debugging
            print("Supabase login failed:", e)

        return Response({
            "message": "Login successful",
            "email": user.email,
            "username": user.username,
            "user_id": user.id,
            "django_access": str(refresh.access_token),
            "django_refresh": str(refresh),
            "supabase_access_token": access_token
        }, status=status.HTTP_200_OK)


# ----------------------------
# LOGOUT USER
# ----------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        access_token = request.data.get("access_token")

        # Supabase logout
        try:
            if access_token:
                supabase.auth.sign_out()
        except Exception:
            pass

        # Django logout
        request.session.flush()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


# ----------------------------
# PASSWORD RESET (REQUEST)
# ----------------------------
class PasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Send Supabase reset email. Ensure redirect_to matches your frontend Reset page.
            supabase.auth.reset_password_email(email, options={
                "redirect_to": "https://social-media-frontend-git-main-rishabhrawat12345s-projects.vercel.app/Reset-password"
            })
            return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------
# PASSWORD RESET CONFIRM
# ----------------------------
class PasswordResetConfirmView(APIView):
    """
    Receives a Supabase access_token (from the password reset link) and new_password.
    Uses supabase.auth.update_user to set the new Supabase password, then updates Django user.
    Returns string errors (never raw objects) to make frontend rendering safe.
    """
    def post(self, request):
        access_token = request.data.get("access_token")
        new_password = request.data.get("new_password")

        if not access_token or not new_password:
            return Response({"error": "Access token and new password required"}, status=status.HTTP_400_BAD_REQUEST)

        # Use supabase client update_user, passing the access token
        try:
            # supabase.auth.update_user returns an object or dict depending on client version
            sup_resp = supabase.auth.update_user({"password": new_password}, access_token=access_token)
        except Exception as e:
            # Return safe string message
            return Response({"error": f"Failed to update Supabase user: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Extract response safely
        try:
            sup_user = None
            # sup_resp may be a dict with "user" or an object with .user
            if isinstance(sup_resp, dict):
                sup_user = sup_resp.get("user")
                sup_error = sup_resp.get("error") or sup_resp.get("message")
            else:
                sup_user = getattr(sup_resp, "user", None)
                sup_error = getattr(sup_resp, "error", None) or getattr(sup_resp, "message", None)

            if sup_user is None:
                # If supabase returned an error, extract message from response or fallback
                # Convert sup_resp to string safely for message
                try:
                    # If sup_resp is requests.Response-like dict
                    error_message = sup_error or str(sup_resp)
                except Exception:
                    error_message = "Failed to change password in Supabase."
                return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

            # sup_user contains user's email. Update Django user password
            user = CustomUser.objects.filter(email=sup_user.email).first()
            if user:
                # Use set_password to ensure correct hashing and other hooks
                user.set_password(new_password)
                user.save()

            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Server error while finalizing password reset: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------
# CHANGE PASSWORD (AUTHENTICATED)
# ----------------------------
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"error": "Old and new password required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Update Django password
            user.set_password(new_password)
            user.save()

            # Attempt to update Supabase password if possible (best-effort)
            try:
                # If you have a way to get the user's supabase session/access token, use it.
                # Here we attempt to get a supabase user by email (client behavior may vary)
                sup_user_resp = supabase.auth.get_user_by_email(user.email)
                sup_user = getattr(sup_user_resp, "user", None)
                sup_session = getattr(sup_user_resp, "session", None)
                if sup_user and sup_session:
                    supabase.auth.update_user({"password": new_password}, access_token=sup_session.access_token)
            except Exception:
                # not fatal
                pass

            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------
# REFRESH DJANGO JWT TOKEN
# ----------------------------
class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)


class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            users = CustomUser.objects.filter(
                username__icontains=query
            ) | CustomUser.objects.filter(
                first_name__icontains=query
            ) | CustomUser.objects.filter(
                last_name__icontains=query
            )
        else:
            users = CustomUser.objects.none()

        serializer = UserSearchSerializer(users, many=True)
        return Response(serializer.data)
