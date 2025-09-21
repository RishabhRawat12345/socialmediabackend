from rest_framework import generics, permissions, status, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from posts.models import Post
from .models import Like, Comment
from .serializers import CommentSerializer

# Like/Unlike a post
class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        return Response({
            "status": "liked" if created else "already liked",
            "total_likes": post.likes.count()
        })

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        return Response({
            "status": "unliked" if deleted else "not liked",
            "total_likes": post.likes.count()
        })


# Check if user liked post
class LikeStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        liked = Like.objects.filter(user=request.user, post=post).exists()
        return Response({"liked": liked})


# Add comment / Get comments
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'], is_active=True)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)


# Delete own comment
class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise exceptions.PermissionDenied("You can only delete your own comments")
        instance.delete()
