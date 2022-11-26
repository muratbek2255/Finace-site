from rest_framework import serializers

from apps.budget.models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for budget"""
    class Meta:
        model = Budget
        fields = (
            'codename', 'daily_limit'
        )
