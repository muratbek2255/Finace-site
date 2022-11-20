from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin,
    UpdateModelMixin, DestroyModelMixin, CreateModelMixin
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from twilio.rest import Client

from apps.authentication.services import generate_otp
from apps.authentication.tasks import (
    send_activation_code, send_reset_code
)

from apps.users.models import User


class RegistrationMixin:
    """Registration Mixin"""
    model = None
    serializer_class = None
    permission_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = request.query_params.get('email')
        user = get_object_or_404(User, email=email)
        user.is_active = False
        user.create_activation_code()
        user.save()
        send_activation_code.delay(email=user.email, activation_code=user.activation_code)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginMixin:
    """Login Mixin"""
    serializer_class = None
    permission_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendSmsMixin:
    serializer_class = None
    permission_class = None
    otp = None

    @transaction.atomic()
    def post(self, request):
        data = request.data
        email = data['email']
        user = User.objects.get(email=email)
        phone_number_valid = self.serializer_class(data=data)
        if not phone_number_valid.is_valid():
            return Response({'errors': 'Не валидный номер телефона'})

        phone_number = data['phone_number']
        otp = self.otp
        if otp is None:
            otp = generate_otp()

        user.otp_code = otp
        user.phone_number = phone_number
        expiry = timezone.now() + timedelta(minutes=30)
        user.otp_code_expiry = expiry
        user.save()

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message_to_broadcast = f'Твой верификационный код {otp}'
            client.messages.create(to=phone_number,
                                   from_=settings.TWILIO_NUMBER,
                                   body=message_to_broadcast)

            return Response({'message': 'Код был отправлен', 'otp': otp})
        except Exception as exc:
            print(f'we caucht {exc}')
            print(f'we caucht {type(exc)}')
            return Response({'errors': 'Есть некоторые проблемы с отправкой кода'})


class VerifyOtpMixin:
    """Activation from sms"""
    serializer_class = None
    permission_class = None

    def post(self, request):
        data = request.data
        user = User.objects.filter(email=data['email'])

        if not user.exists():
            return Response({'errors': 'Ты не зарегестрирован'})

        user = user[0]

        if user.otp_code != data['otp_code']:
            return Response({'errors': 'Пожайлуста введите валидный код'})

        otp_expired = self.serializer_class(data=data)

        if not otp_expired:
            return Response({'errors': 'Закончился срок годности кода'})

        user.phone_verified = True
        user.save()
        return Response({'message': 'Номер активирован'})


class ForgotPasswordMixin:
    """Forgot password"""

    serializer_class = None
    permission_classes = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.query_params.get('email')

        if User.objects.filter(email=email).exists():
            user = request.user
            user.is_active = False
            user.create_activation_code()
            user.save()
            print(user)
            send_reset_code.delay(email=user.email, activation_code=user.activation_code)
            return Response("Вам отправили сообщение", status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'Could not password, invalid token'},
                            status.HTTP_400_BAD_REQUEST
                            )


class ForgotPasswordCompleteMixin:
    """Create password from email"""
    serializer_class = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Вы успешно восстановили пароль', status=200)
