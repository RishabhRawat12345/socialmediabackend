from rest_framework import serializers
from posts.models import Post

class FeedPostSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'created_at', 
            'likes_count', 'comments_count', 'is_liked_by_user'
        ]

    def get_is_liked_by_user(self, obj):
        user = self.context['request'].user
        return obj.likes.filter(id=user.id).exists()
