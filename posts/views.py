from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from notifications.utils import create_notification

# ---------------- Post Views ----------------
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.filter(is_active=True)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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
        post = Post.objects.get(id=post_id)
        user = request.user

        # Toggle like
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
            # Create notification for post author
            create_notification(
                sender=user,
                recipient=post.author,
                notification_type='like',
                post=post,
                message=f"{user.username} liked your post."
            )

        post.save()
        return Response({"liked": liked, "likes_count": post.likes.count()})

# ---------------- Comment View ----------------
class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)

        # Notify post author
        create_notification(
            sender=self.request.user,
            recipient=comment.post.author,
            notification_type='comment',
            post=comment.post,
            message=f"{self.request.user.username} commented on your post."
        )
