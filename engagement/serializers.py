from rest_framework import serializers
from .models import Like, Comment

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'created_at', 'is_active']
        read_only_fields = ['author', 'post', 'created_at', 'is_active']
