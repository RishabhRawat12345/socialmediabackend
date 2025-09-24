# notifications/views.py
from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Notification
from .serializers import NotificationSerializer

User = get_user_model()

# List all notifications for the authenticated user
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')


# Mark a single notification as read
@api_view(['POST'])
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=404)


# Mark all notifications as read
@api_view(['POST'])
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({'status': 'all notifications marked as read'})


# Create a new notification
@api_view(['POST'])
def create_notification(request):
    """
    Create a new notification.
    Expected payload:
    {
        "recipient_id": 1,
        "message": "You have a new message",
        "type": "info"  # optional
    }
    """
    recipient_id = request.data.get('recipient_id')
    message = request.data.get('message')
    notif_type = request.data.get('type', 'info')  # default type if not provided

    if not recipient_id or not message:
        return Response({'error': 'recipient_id and message are required'}, status=400)
    
    try:
        recipient = User.objects.get(id=recipient_id)
        notification = Notification.objects.create(
            recipient=recipient,
            message=message,
            type=notif_type
        )
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=201)
    except User.DoesNotExist:
        return Response({'error': 'Recipient user not found'}, status=404)
