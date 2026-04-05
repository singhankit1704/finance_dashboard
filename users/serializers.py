from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for reading user data (safe fields only)."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user (admin only)."""
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'role', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user role/status (admin only)."""

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'is_active']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
