from rest_framework import generics, permissions
from django.db.models import Q
from posts.models import Post
from followers.models import Follow
from .serializers import FeedPostSerializer
from .pagination import FeedPagination

class FeedListView(generics.ListAPIView):
    serializer_class = FeedPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FeedPagination

    def get_queryset(self):
        user = self.request.user
        # Get IDs of followed users
        following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
        # Get posts from followed users + own posts
        posts = Post.objects.filter(
            Q(author__in=following_users) | Q(author=user)
        ).order_by('-created_at')
        return posts
