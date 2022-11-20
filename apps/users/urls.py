from django.urls import path

from apps.users.views import UserAPIViewSet

urlpatterns = [
    path('users/all/', UserAPIViewSet.as_view({'get': 'list'})),
    path('user/<int:pk>/', UserAPIViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
]
