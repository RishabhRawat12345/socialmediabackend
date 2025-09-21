# profiles/models.py
from django.db import models
from users.models import CustomUser

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    profile_visibility = models.BooleanField(default=True)
    avatar_url = models.URLField(blank=True, null=True)  # Supabase public URL
    def __str__(self):
        return f"{self.user.username}'s profile"
