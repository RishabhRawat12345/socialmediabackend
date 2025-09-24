from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from followers.models import Follow  # Your follow model
from posts.models import Post, Comment
from .models import Notification

# ---------------------------
# Follow notifications
# ---------------------------
@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.following,
            sender=instance.follower,
            notification_type='follow',
            message=f"{instance.follower.username} started following you."
        )

# ---------------------------
# Comment notifications
# ---------------------------
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

# ---------------------------
# Like notifications
# ---------------------------
@receiver(m2m_changed, sender=Post.likes.through)
def create_like_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            if instance.author.id != user_id:
                Notification.objects.create(
                    recipient=instance.author,
                    sender_id=user_id,
                    post=instance,
                    notification_type='like',
                    message=f"{instance.likes.get(id=user_id).username} liked your post."
                )
