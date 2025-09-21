from rest_framework import serializers
import re
from .models import CustomUser
from .supabase_client import supabase

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
        # Check in Django DB
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        
        # Optional: Check in Supabase (requires service role key)
        try:
            user_response = supabase.auth.admin.get_user_by_email(value)
            if user_response.get("user"):
                raise serializers.ValidationError("Email already exists in Supabase")
        except Exception:
            pass  # ignore network or permission errors
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

        if not response.user:
            raise serializers.ValidationError("Supabase signup failed")

        # Save user in Django DB (inactive until email verification)
        user = CustomUser.objects.create(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            is_active=False
        )
        user.set_password(validated_data["password"])  # hash and save
        user.save()
        return user



