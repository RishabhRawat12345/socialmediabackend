from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Post, Comment, Like, Notification
from .serializers import PostSerializer, CommentSerializer, NotificationSerializer
from .utils import create_notification  # ensure this exists


# ---------------- Post Views ----------------

class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.filter(is_active=True)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.filter(is_active=True)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.author:
            raise PermissionDenied("You can only update your own post")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise PermissionDenied("You can only delete your own post")
        instance.delete()


class MyPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user, is_active=True)


# ---------------- Comment Views ----------------

class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)
        return Comment.objects.filter(post=post).order_by('-created_at')


class CommentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if not post.is_active:
            return Response({"error": "Cannot comment on an inactive post."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(author=request.user, post=post)

            # Notification for post owner
            if post.author != request.user:
                create_notification(
                    sender=request.user,
                    recipient=post.author,
                    notification_type='comment',
                    post=post,
                    message=f"{request.user.username} commented on your post."
                )

            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- Like Post View ----------------

class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        like_obj, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            like_obj.delete()
            liked = False
        else:
            liked = True
            if post.author != user:
                create_notification(
                    sender=user,
                    recipient=post.author,
                    notification_type='like',
                    post=post,
                    message=f"{user.username} liked your post."
                )

        likes_count = post.likes.count()
        return Response({"liked": liked, "likes_count": likes_count})


# ---------------- Notifications ----------------

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.read = True
        notification.save()
        return Response({"status": "Notification marked as read"})
