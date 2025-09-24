from django.db.models.signals import post_save
from django.dispatch import receiver
from posts.models import Post
from users.models import CustomUser
from .models import Notification, Follow

# Import Comment if exists
try:
    from posts.models import Comment
except ImportError:
    Comment = None

# Follow notification
@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created and instance.follower != instance.following:
        Notification.objects.create(
            recipient=instance.following,
            sender=instance.follower,
            notification_type='follow',
            message=f"{instance.follower.username} started following you."
        )

# Like notification
@receiver(post_save, sender=Post)
def create_like_notification(sender, instance, **kwargs):
    if hasattr(instance, 'likes'):  # check if likes field exists
        for user in instance.likes.all():
            if user != instance.author:
                Notification.objects.get_or_create(
                    recipient=instance.author,
                    sender=user,
                    post=instance,
                    notification_type='like',
                    message=f"{user.username} liked your post."
                )

# Comment notification (optional if Comment exists)
if Comment:
    @receiver(post_save, sender=Comment)
    def create_comment_notification(sender, instance, created, **kwargs):
        if created and instance.author != instance.post.author:
            Notification.objects.create(
                recipient=instance.post.author,
                sender=instance.author,
                post=instance.post,
                notification_type='comment',
                message=f"{instance.author.username} commented on your post."
            )
