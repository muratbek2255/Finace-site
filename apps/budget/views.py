from rest_framework import viewsets

from apps.budget.models import Budget
from apps.budget.serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    """CRUD for budget"""
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

    def perform_create(self, serializer):
        serializer.save()
