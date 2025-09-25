from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Post, Comment, Like, Notification
from .serializers import PostSerializer, CommentSerializer, NotificationSerializer
from .utils import create_notification  # make sure this is correct


# ---------------- Post Views ----------------

class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        # Only allow comments for active posts
        post = get_object_or_404(Post, id=post_id, is_active=True)
        return Comment.objects.filter(post=post).order_by('-created_at')


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_active=True)  # Active post only
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



# ---------------- Comment Views ----------------
class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = serializer.validated_data['post']
        if not post.is_active:
            raise PermissionDenied("Cannot comment on an inactive post.")

        comment = serializer.save(author=self.request.user)

        if comment.post.author != self.request.user:
            create_notification(
                sender=self.request.user,
                recipient=comment.post.author,
                notification_type='comment',
                post=comment.post,
                message=f"{self.request.user.username} commented on your post."
            )


class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)
        return Comment.objects.filter(post=post).order_by('-created_at')


# ---------------- My Posts ----------------
class MyPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user, is_active=True)


# ---------------- Notifications ----------------
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.read = True
        notification.save()
        return Response({"status": "Notification marked as read"})
