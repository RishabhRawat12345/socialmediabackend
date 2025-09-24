from django.db import models
from users.models import CustomUser
from posts.models import Post

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('comment', 'Comment'),
    ]

    recipient = models.ForeignKey(
        CustomUser,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.recipient} [{self.notification_type}]"
