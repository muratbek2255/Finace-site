from django.urls import path

from apps.authentication.views import (
    UserRegistrationView, UserLoginView, UserLoginOutView,
    ChangePasswordView, UpdateProfileView,
    SendSmsView, VerifyOtpView, DeleteAccountAPIView,
    ActivateView, ForgotPasswordView, ForgotPasswordCompleteView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='auth_register'),
    path('activate/<str:activation_code>/', ActivateView.as_view()),
    path('login/', UserLoginView.as_view(), name='auth_login'),
    path('logout/', UserLoginOutView.as_view(), name='auth_logout'),
    path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('forgot_password/', ForgotPasswordView.as_view()),
    path('forgot_password_complete/', ForgotPasswordCompleteView.as_view()),
    path('update_profile/<int:pk>/', UpdateProfileView.as_view(), name='auth_update_profile'),
    path('delete_profile/<int:pk>/', DeleteAccountAPIView.as_view(), name='delete_profile'),
    path('send-sms/', SendSmsView.as_view(), name='send-sms'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp')
]
