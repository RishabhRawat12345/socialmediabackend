from rest_framework import serializers
import re
from .models import CustomUser
from .supabase_client import supabase
from posts.models import Post


# --------------------------
# REGISTER SERIALIZER
# --------------------------
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', value):
            raise serializers.ValidationError(
                "Username must be 3-30 chars, alphanumeric + underscore"
            )
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists in Django")

        try:
            user_response = supabase.auth.admin.get_user_by_email(value)
            if user_response.get("user"):
                raise serializers.ValidationError("Email already exists in Supabase")
        except Exception:
            pass  # ignore errors
        return value

    def create(self, validated_data):
        try:
            # Sign up in Supabase
            credentials = {
                "email": validated_data["email"],
                "password": validated_data["password"],
                "options": {
                    "data": {
                        "username": validated_data["username"],
                        "first_name": validated_data["first_name"],
                        "last_name": validated_data["last_name"],
                    }
                }
            }
            response = supabase.auth.sign_up(credentials)
        except Exception as e:
            raise serializers.ValidationError(f"Supabase signup failed: {str(e)}")

        if not getattr(response, "user", None):
            raise serializers.ValidationError("Supabase signup failed")

        # Save user in Django DB (inactive until email verification)
        user = CustomUser.objects.create(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            is_active=True
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


# --------------------------
# USER SEARCH SERIALIZER
# --------------------------
class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar']


# --------------------------
# ADMIN USER SERIALIZER
# --------------------------
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']


# --------------------------
# ADMIN USER UPDATE SERIALIZER (PATCH/PUT)
# --------------------------
class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['is_active', 'is_staff']  # only these fields can be updated via admin


# --------------------------
# POST SERIALIZER
# --------------------------
class AdminPostSerializer(serializers.ModelSerializer):
    total_likes = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image_url', 'is_active', 'total_likes', 'total_comments']

    def get_total_likes(self, obj):
        # Replace 'likes' with the related_name from your Post -> Like relationship
        return obj.likes.count() if hasattr(obj, 'likes') else 0

    def get_total_comments(self, obj):
        # Replace 'comments' with the related_name from your Post -> Comment relationship
        return obj.comments.count() if hasattr(obj, 'comments') else 0


# --------------------------
# ADMIN POST UPDATE SERIALIZER
# --------------------------
class AdminPostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['is_active']  # only active status can be updated
