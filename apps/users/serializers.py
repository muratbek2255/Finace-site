from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user"""
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'last_name', 'first_name', 'password',
            'phone_number'
        )
