from rest_framework import serializers
from .models import Follow

class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.CharField(source='follower.username', read_only=True)
    following = serializers.CharField(source='following.username', read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
