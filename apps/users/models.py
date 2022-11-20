from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string

from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.managers import UserManager


class AbstractTimeStampModel(models.Model):
    """This model for date, when created and updated"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    """Custom User"""
    email = models.EmailField('Email', unique=True)
    first_name = models.CharField('Name', max_length=125)
    last_name = models.CharField('Surname', max_length=125)
    phone_number = models.CharField("Phone number", max_length=127, unique=True)
    otp_code = models.CharField("Otp code", max_length=30, null=True)
    activation_code = models.CharField("For activation code", max_length=50, blank=True)

    objects = UserManager()

    def tokens(self):
        refresh = RefreshToken()
        return {
            refresh: str(refresh),
            'access': str(refresh.access_token)
        }

    def __str__(self):
        return f"id: {self.id}, email: {self.email}"

    def create_activation_code(self):
        code = get_random_string(6, allowed_chars='123456789')
        self.activation_code = code

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
