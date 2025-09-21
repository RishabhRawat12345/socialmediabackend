from rest_framework import serializers
from users.models import CustomUser
from posts.models import Post

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff']

class AdminPostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'author', 'author_username', 'content', 'created_at']
