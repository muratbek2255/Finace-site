from rest_framework.routers import DefaultRouter

from apps.budget.views import BudgetViewSet

router = DefaultRouter()
router.register(r'budgets', BudgetViewSet)

urlpatterns = router.urls
