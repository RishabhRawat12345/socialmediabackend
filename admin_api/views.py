from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from posts.models import Post
from .permissions import IsAdminUser

User = get_user_model()

# ------------------ USER MANAGEMENT ------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_users(request):
    users = User.objects.all().values("id", "username", "email", "is_active", "is_staff", "date_joined")
    return Response(users, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_details(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "date_joined": user.date_joined,
        }
        return Response(data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def deactivate_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()
        return Response({"message": f"User {user.username} deactivated"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# ------------------ CONTENT MANAGEMENT ------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_posts(request):
    posts = Post.objects.all().values("id", "author_id", "content", "created_at")
    return Response(posts, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return Response({"message": "Post deleted successfully"}, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)


# ------------------ BASIC STATISTICS ------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def stats(request):
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    active_today = User.objects.filter(last_login__date=now().date()).count()

    return Response({
        "total_users": total_users,
        "total_posts": total_posts,
        "active_today": active_today,
    }, status=status.HTTP_200_OK)
