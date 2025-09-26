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
            supabase_user = user_info.user
        except Exception as e:
            return Response({"error": f"Failed to fetch user from Supabase: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not supabase_user:
            return Response({"error": "Invalid Supabase user"}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(email=supabase_user.email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if supabase_user.confirmed_at:
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
            if supabase_response and supabase_response.session:
                access_token = supabase_response.session.access_token
        except Exception as e:
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
            supabase.auth.reset_password_email(email, options={
                "redirect_to": "http://localhost:3000/reset-password"
            })
            return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------
# PASSWORD RESET CONFIRM
# ----------------------------
class PasswordResetConfirmView(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        new_password = request.data.get("new_password")

        if not access_token or not new_password:
            return Response({"error": "Access token and new password required"}, status=status.HTTP_400_BAD_REQUEST)

        url = f"{SUPABASE_URL}/auth/v1/user"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {"password": new_password}

        try:
            resp = requests.put(url, json=payload, headers=headers)
            if resp.status_code == 200:
                # Update Django password
                supabase_user_info = supabase.auth.get_user(access_token)
                user = CustomUser.objects.filter(email=supabase_user_info.user.email).first()
                if user:
                    user.password = make_password(new_password)
                    user.save()
                return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": resp.json()}, status=resp.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            user.password = make_password(new_password)
            user.save()

            # Update Supabase password
            supabase_user = supabase.auth.get_user_by_email(user.email)
            if supabase_user and supabase_user.session:
                supabase.auth.update_user({"password": new_password}, access_token=supabase_user.session.access_token)

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
