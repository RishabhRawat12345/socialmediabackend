from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from posts.models import Post
from .models import Like, Comment
from .serializers import PostSerializer, CommentSerializer


# Get all posts with likes & comments
class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')

    def get_serializer_context(self):
        return {"request": self.request}


# Get details of a single post with likes & comments
class PostDetailView(generics.RetrieveAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()

    def get_serializer_context(self):
        return {"request": self.request}


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


# Add/Get comments for a post
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'], is_active=True)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)
