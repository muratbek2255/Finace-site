from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.response import Response
from twilio.rest import Client

from apps.authentication.services import generate_otp
from apps.authentication.tasks import (
    send_activation_code, send_reset_code
)

from apps.users.models import User


class RegistrationMixin(GenericAPIView):
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
            return Response({'errors': 'Not valid phone number'})

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
            message_to_broadcast = f'Your verification code: {otp}'
            client.messages.create(to=phone_number,
                                   from_=settings.TWILIO_NUMBER,
                                   body=message_to_broadcast)

            return Response({'message': 'Code has been sent', 'otp': otp})
        except Exception as exc:
            print(f'we caucht {exc}')
            print(f'we caucht {type(exc)}')
            return Response({'errors': 'There are some problems with submitting the code'})


class VerifyOtpMixin:
    """Activation from sms"""
    serializer_class = None
    permission_class = None

    def post(self, request):
        data = request.data
        user = User.objects.filter(email=data['email'])

        if not user.exists():
            return Response({'errors': 'You are not registered'})

        user = user[0]

        if user.otp_code != data['otp_code']:
            return Response({'errors': 'Please enter a valid code'})

        otp_expired = self.serializer_class(data=data)

        if not otp_expired:
            return Response({'errors': 'Code expired'})

        user.phone_verified = True
        user.save()
        return Response({'message': 'Number activated'})


class ForgotPasswordMixin:

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
            return Response("You have been sent a message", status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'Could not password, invalid token'},
                            status.HTTP_400_BAD_REQUEST
                            )


class ForgotPasswordCompleteMixin:
    serializer_class = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('You have successfully recovered your password', status=200)
