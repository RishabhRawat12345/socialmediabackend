# notifications/serializers.py
from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    post_content = serializers.CharField(source='post.content', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'sender', 'sender_username', 'notification_type', 'post', 'post_content', 'message', 'is_read', 'created_at']
