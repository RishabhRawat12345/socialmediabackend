from django.db import models
from django.conf import settings
from posts.models import Post

# ---------------- Engagement Like ----------------
class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_engagement_likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='engagement_likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

# ---------------- Engagement Comment ----------------
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='engagement_comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_engagement_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
