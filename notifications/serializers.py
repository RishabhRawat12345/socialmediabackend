from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    read = serializers.BooleanField(source='is_read')

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'read', 'created_at']

    def get_title(self, obj):
        if obj.notification_type == 'follow':
            return 'New Follower'
        if obj.notification_type == 'like':
            return 'New Like'
        if obj.notification_type == 'comment':
            return 'New Comment'
        return 'Notification'
