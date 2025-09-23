from rest_framework import serializers
from .models import UserProfile
from .supabase_client import supabase  # Make sure this exists
import mimetypes

class UserProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    # Upload field
    avatar = serializers.ImageField(write_only=True, required=False)
    avatar_url = serializers.URLField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'username', 'user_email',
            'bio', 'location', 'website', 'profile_visibility',
            'avatar', 'avatar_url'
        ]
        read_only_fields = ['user', 'username', 'user_email', 'avatar_url']

    def validate_avatar(self, value):
        if value.size > 2 * 1024 * 1024:  # 2MB limit
            raise serializers.ValidationError("Avatar size must be <= 2MB")
        mime_type, _ = mimetypes.guess_type(value.name)
        if mime_type not in ["image/jpeg", "image/png"]:
            raise serializers.ValidationError("Only JPG and PNG images are allowed")
        return value

    def update(self, instance, validated_data):
        avatar = validated_data.pop("avatar", None)

        # Update avatar first
        if avatar:
            file_bytes = avatar.read()
            file_name = f"avatars/{instance.user.id}_{avatar.name}"

            # Upload to Supabase Storage — upsert must be string "true"
            bucket = "avatars"
            supabase.storage.from_(bucket).upload(file_name, file_bytes, {"upsert": "true"})

            # Get public URL
            public_url = supabase.storage.from_(bucket).get_public_url(file_name)
            instance.avatar_url = public_url

        # Update other fields (bio, location, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save instance
        instance.save()
        return instance
