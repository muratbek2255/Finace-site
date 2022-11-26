from rest_framework import serializers

from apps.expenses.models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for expense"""
    class Meta:
        model = Expense
        fields = (
            'amount', 'created_at' 
            'category_codename',  'raw_text'
        )
