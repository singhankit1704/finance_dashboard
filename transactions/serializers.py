from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Full transaction serializer for read operations."""
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'type', 'category', 'date',
            'description', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def get_created_by(self, obj):
        return obj.user.username


class TransactionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating transactions."""

    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'type', 'category', 'date', 'description']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        return value
