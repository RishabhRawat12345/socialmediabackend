from django.db.models.signals import post_save
from django.dispatch import receiver
from followers.models import Follow  # your follow model
from posts.models import Post, Comment  # your post/comment models
from notifications.models import Notification

# Follow notification
@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created and instance.follower != instance.following:
        Notification.objects.create(
            sender=instance.follower,
            recipient=instance.following,
            notification_type='follow',
            message=f"{instance.follower.username} started following you"
        )

# Like notification
@receiver(post_save, sender=Post.likes.through)  # if using ManyToManyField for likes
def create_like_notification(sender, instance, created, **kwargs):
    post = instance.post
    user = instance.user
    if created and post.author != user:
        Notification.objects.create(
            sender=user,
            recipient=post.author,
            notification_type='like',
            post=post,
            message=f"{user.username} liked your post"
        )

# Comment notification
@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.author != instance.post.author:
        Notification.objects.create(
            sender=instance.author,
            recipient=instance.post.author,
            notification_type='comment',
            post=instance.post,
            message=f"{instance.author.username} commented on your post"
        )
