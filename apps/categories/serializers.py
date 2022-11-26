from rest_framework import serializers

from apps.categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category"""
    class Meta:
        model = Category
        fields = (
            'codename', 'name',
            'is_base_expense', 'aliases'
        )
