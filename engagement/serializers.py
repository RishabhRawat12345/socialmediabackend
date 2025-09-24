from rest_framework import serializers
from posts.models import Post
from .models import Like, Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'created_at', 'is_active']
        read_only_fields = ['author', 'post', 'created_at', 'is_active']


class PostSerializer(serializers.ModelSerializer):
    total_likes = serializers.IntegerField(source="likes.count", read_only=True)
    total_comments = serializers.IntegerField(source="comments.count", read_only=True)
    liked = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'image_url', 'created_at',
            'total_likes', 'total_comments', 'liked', 'comments'
        ]

    def get_liked(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False
