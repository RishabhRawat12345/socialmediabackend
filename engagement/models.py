from django.db import models
from django.conf import settings
from posts.models import Post


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes_given"  # all likes by a user
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"  # all likes on a post
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} likes Post {self.post.id}"


class Comment(models.Model):
    content = models.TextField(max_length=200)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments_given"  # all comments by a user
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"  # all comments on a post
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"
