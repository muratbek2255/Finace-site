from django.contrib.auth import get_user_model
from rest_framework import (
    permissions, generics, views, status
)
from rest_framework.response import Response

from apps.authentication.mixins import (
    RegistrationMixin, LoginMixin, SendSmsMixin,
    VerifyOtpMixin, ForgotPasswordCompleteMixin, ForgotPasswordMixin
)
from apps.authentication.serializers import (
    UserRegistrationSerializer, LoginSerializer, LogOutSerializer,
    ChangePasswordSerializer, UpdateUserSerializer,
    OtpSerializer, PhoneNumberSerializer, CreateNewPasswordSerializerAfterReset, ResetPasswordEmailRequestSerializer
)


User = get_user_model()


class UserRegistrationView(RegistrationMixin, views.APIView):
    """Registration user"""
    model = User
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny, )


class UserLoginView(LoginMixin, views.APIView):
    """Login"""
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny, )


class UserLoginOutView(generics.CreateAPIView):
    """Log Out"""
    queryset = User.objects.all()
    serializer_class = LogOutSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        serializer.save()


class ChangePasswordView(generics.UpdateAPIView):
    """Update password"""
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ChangePasswordSerializer

    def perform_update(self, serializer):
        serializer.save()


class UpdateProfileView(generics.UpdateAPIView):
    """Update profile"""
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UpdateUserSerializer

    def perform_update(self, serializer):
        serializer.save()


class SendSmsView(SendSmsMixin, views.APIView):
    """Verification code"""
    serializer_class = PhoneNumberSerializer
    permission_class = (permissions.AllowAny, )


class VerifyOtpView(VerifyOtpMixin, views.APIView):
    """Activation from sms"""
    serializer_class = OtpSerializer
    permission_class = (permissions.AllowAny,)


class DeleteAccountAPIView(views.APIView):
    """Delete user"""
    permission_classes = [permissions.IsAuthenticated, ]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({"message": "Данный пользователь был удален"})


class ActivateView(views.APIView):
    """Activation from email"""
    def get(self, request, activation_code):
        user = User()
        user.is_active = True
        user.activation_code = activation_code
        user.save()
        return Response('Your account successfully activated!', status=status.HTTP_200_OK)


class ForgotPasswordView(ForgotPasswordMixin, views.APIView):
    """Forgot password"""

    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = (permissions.IsAuthenticated, )


class ForgotPasswordCompleteView(ForgotPasswordCompleteMixin, views.APIView):
    """Create password from email"""
    serializer_class = CreateNewPasswordSerializerAfterReset
