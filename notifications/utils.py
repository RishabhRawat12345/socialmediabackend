from .models import Notification

def create_notification(sender, recipient, notification_type, post=None, message=""):
    if sender == recipient:
        return  # Don't notify yourself
    Notification.objects.create(
        sender=sender,
        recipient=recipient,
        notification_type=notification_type,
        post=post,
        message=message
    )

