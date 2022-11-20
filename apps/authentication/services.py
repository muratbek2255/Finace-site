from random import randint

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def generate_otp() -> str:
    range_start = 10 ** (6 - 1)
    range_end = (10 ** 6) - 1
    otp = randint(range_start, range_end)
    otp = str(otp)
    return otp


def get_tokens_for_user(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}
