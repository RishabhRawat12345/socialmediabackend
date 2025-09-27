import os
import requests
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .models import CustomUser
from posts.models import Post
from .serializers import (
    RegisterSerializer,
    UserSearchSerializer,
    AdminUserSerializer,
    AdminPostSerializer
)
from .supabase_client import supabase

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
# LOGIN USER
# ----------------------------
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")

        if not password or (not email and not username):
            return Response({"error": "Username/Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if email:
                user_obj = User.objects.get(email=email)
            else:
                user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(request, username=user_obj.get_username(), password=password)
        if not user or not user.is_active:
            return Response({"error": "Invalid credentials or user not active"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = None

        try:
            supabase_response = supabase.auth.sign_in_with_password({"email": user.email, "password": password})
            if supabase_response and getattr(supabase_response, "session", None):
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
# ADMIN: LIST ALL USERS
# ----------------------------
class AdminUsersListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ----------------------------
# ADMIN: USER DETAIL & UPDATE
# ----------------------------
class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSearchSerializer(user)
        return Response(serializer.data)

    def put(self, request, user_id):
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSearchSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------
# ADMIN: LIST ALL POSTS
# ----------------------------
class AdminPostsListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        posts = Post.objects.all()
        serializer = AdminPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ----------------------------
# ADMIN: UPDATE POST (ACTIVATE/DEACTIVATE)
# ----------------------------
class AdminPostUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, post_id):
        return self.update_post(request, post_id)

    def patch(self, request, post_id):
        return self.update_post(request, post_id)

    def update_post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        is_active = request.data.get("is_active")
        if is_active is not None:
            post.is_active = is_active
            post.save()
            return Response({"message": "Post updated successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "is_active field required"}, status=status.HTTP_400_BAD_REQUEST)
