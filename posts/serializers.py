from rest_framework import serializers
from .models import Post, Like, Comment, Notification
from .supabase_client import supabase
import mimetypes

# ---------------- Post Serializer ----------------
class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    image = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.URLField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    total_likes = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'category',
            'image', 'image_url',
            'created_at', 'updated_at',
            'total_likes', 'total_comments', 'liked',
            'is_active'
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
            {"upsert": "true", "content-type": mime_type or "application/octet-stream"},
        )
        return supabase.storage.from_(bucket).get_public_url(file_name)

    def create(self, validated_data):
        validated_data['is_active'] = True
        image = validated_data.pop('image', None)
        post = Post.objects.create(**validated_data)

        if image:
            post.image_url = self.upload_image_to_supabase(post.id, image)
            post.save()
        return post

    def update(self, instance, validated_data):
        validated_data['is_active'] = True
        image = validated_data.pop('image', None)
        instance = super().update(instance, validated_data)

        if image:
            instance.image_url = self.upload_image_to_supabase(instance.id, image)
            instance.save()
        return instance

    def get_total_likes(self, obj):
        return obj.post_likes.count()

    def get_total_comments(self, obj):
        return obj.comments.count()

    def get_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.post_likes.filter(user=request.user).exists()
        return False

# ---------------- Comment Serializer ----------------
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'content', 'created_at']

# ---------------- Notification Serializer ----------------
class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    post_id = serializers.IntegerField(source='post.id', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'sender_username', 'post_id', 'message', 'read', 'created_at']
