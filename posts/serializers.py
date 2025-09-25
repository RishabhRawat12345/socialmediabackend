from rest_framework import serializers
from .models import Post, Comment
from .supabase_client import supabase
import mimetypes
from .models import Notification

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    image = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.URLField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)  # Always read-only

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'category', 'image', 'image_url',
            'created_at', 'updated_at', 'like_count', 'comment_count', 'is_active'
        ]

    def validate_image(self, value):
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image size must be <= 2MB")
        mime_type, _ = mimetypes.guess_type(value.name)
        if mime_type not in ["image/jpeg", "image/png"]:
            raise serializers.ValidationError("Only JPG and PNG images are allowed")
        return value

    def upload_image_to_supabase(self, post_id, image):
        file_bytes = image.read()
        mime_type, _ = mimetypes.guess_type(image.name)
        file_name = f"posts/{post_id}_{image.name}"
        bucket = "posts"

        supabase.storage.from_(bucket).upload(
            file_name,
            file_bytes,
            {
                "upsert": "true",
                "content-type": mime_type or "application/octet-stream",
            },
        )

        return supabase.storage.from_(bucket).get_public_url(file_name)

    def create(self, validated_data):
        validated_data['is_active'] = True  # Force is_active to True
        image = validated_data.pop('image', None)
        post = Post.objects.create(**validated_data)

        if image:
            post.image_url = self.upload_image_to_supabase(post.id, image)
            post.save()

        return post

    def update(self, instance, validated_data):
        validated_data['is_active'] = True  # Keep is_active True on update
        image = validated_data.pop('image', None)
        instance = super().update(instance, validated_data)

        if image:
            instance.image_url = self.upload_image_to_supabase(instance.id, image)
            instance.save()

        return instance
        


# serializers.py
from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'post', 'created_at']



class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id", "sender_username", "message",
            "notification_type", "post", "read", "created_at"
        ]
