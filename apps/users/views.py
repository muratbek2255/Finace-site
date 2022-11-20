from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions

from apps.users.serializers import UserSerializer

User = get_user_model()


class UserAPIViewSet(viewsets.ModelViewSet):
    """Output all users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser, )
