from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer
from notifications.utils import create_notification
from .utils import create_notification


# ---------------- Post Views ----------------
class PostListCreateView(generics.ListCreateAPIView):
    """
    List all active posts or create a new post
    """
    queryset = Post.objects.filter(is_active=True)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a post
    """
    queryset = Post.objects.all()
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


# ---------------- Like Post View ----------------
class LikePostView(APIView):
    """
    Toggle like/unlike for a post
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        # Check if like exists
        like_obj, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            # User already liked -> remove like
            like_obj.delete()
            liked = False
        else:
            liked = True
            # Send notification to post author
            if post.author != user:  # Avoid notifying self
                create_notification(
                    sender=user,
                    recipient=post.author,
                    notification_type='like',
                    post=post,
                    message=f"{user.username} liked your post."
                )

        # Count likes
        likes_count = post.likes.count()
        return Response({"liked": liked, "likes_count": likes_count})


# ---------------- Comment View ----------------
class CommentCreateView(generics.CreateAPIView):
    """
    Create a comment for a post
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)

        # Notify post author if commenter is not the author
        if comment.post.author != self.request.user:
            create_notification(
                sender=self.request.user,
                recipient=comment.post.author,
                notification_type='comment',
                post=comment.post,
                message=f"{self.request.user.username} commented on your post."
            )


# ---------------- My Posts View (optional) ----------------
class MyPostListView(generics.ListAPIView):
    """
    List all posts created by the logged-in user
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user, is_active=True)


from .models import Notification
from .serializers import NotificationSerializer

# ---------------- Notifications ----------------
class NotificationListView(generics.ListAPIView):
    """
    List all notifications for the logged-in user
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class MarkNotificationReadView(APIView):
    """
    Mark a notification as read
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
            notification.read = True
            notification.save()
            return Response({"status": "Notification marked as read"})
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)

