from django.contrib import auth
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.services import get_tokens_for_user
from apps.authentication.tasks import send_activation_code

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):

    default_error_messages = {
        'username': 'username received only alphanumeric characters'
    }
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, user):
        tokens = get_tokens_for_user(user)
        return tokens

    class Meta:
        model = User
        fields = (
           'id', 'email', 'username',
           'password', 'first_name', 'last_name',
           'phone_number', 'tokens'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number']
        )
        user.set_password(validated_data['password'])
        user.save()
        user.create_activation_code()
        send_activation_code.delay(email=user.email, activation_code=user.activation_code)
        return user

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')

        if not username.isalnum():
            raise serializers.ValidationError(
                self.default_error_messages)
        return attrs

    def validate_password(self, value):
        if len(value) < 8:
            raise ValueError('Password is too small')
        elif len(value) > 30:
            raise ValueError('Password is too big')
        else:
            return value


class LoginSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        max_length=68, min_length=6, write_only=True
    )
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True
    )

    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(phone_number=obj['phone_number'])
        tokens = get_tokens_for_user(user)
        return tokens

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'tokens']

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        user = auth.authenticate(phone_number=phone_number, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, please try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact administrator')

        return {
            'phone_number': user.phone_number,
            'tokens': user.tokens
        }


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': 'Token expired or invalid'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "The password fields do not match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is incorrect"})
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'phone_number'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email already exists!"})
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError({"username": "This nickname already exists!"})
        return value

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.username = validated_data['username']
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.phone_number = validated_data['phone_number']

        instance.save()

        return instance


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False)
    email = serializers.EmailField(max_length=255, min_length=3)

    class Meta:
        fields = ['phone_number', 'email']

    def validate(self, data):
        phone_number_valid = 'phone_number' in data and data['phone_number']

        if not phone_number_valid:
            return Response({'error': 'Please write correct!!!'})

        return data


class OtpSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=20)
    otp_code = serializers.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['email', 'otp_code']

    def validate(self, data):
        user = User.objects.filter(otp_code=data['otp_code'])

        if not user.exists():
            return Response({'errors': ' Please write valid code'})

        expiry_time = user[0].otp_code_expiry
        if expiry_time > timezone:
            return Response({'otp': data['otp_code']})
        return Response({'errors': 'Code expired'})


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        model = User
        fields = ['email']


class CreateNewPasswordSerializerAfterReset(serializers.Serializer):
    email = serializers.EmailField(max_length=500, required=True)
    activation_code = serializers.CharField(max_length=6, min_length=6, required=True)
    password = serializers.CharField(min_length=8, required=True)
    password_confirm = serializers.CharField(min_length=8, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'activation_code')

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('User does not exist')
        return email

    def validate_activation_code(self, code):
        if not User.objects.filter(activation_code=code, is_active=False).exists():
            raise serializers.ValidationError('Incorrect activation code')
        return code

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        return attrs

    def save(self, **kwargs):
        print(self.validated_data)
        data = self.validated_data
        email = data.get('email')
        print(email)
        code = data.get('activation_code')
        password = data.get('password')
        try:
            user = User.objects.filter(
                email=email,
                activation_code=code,
                is_active=False
            )[0]
            print(user)
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist')
        user.is_active = True
        print(user.is_active)
        user.activation_code = ''
        print(user.activation_code)
        user.set_password(password)
        user.save()
