from datetime import datetime, timedelta

from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "expire_time": datetime.now()
                       + settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")
                       - timedelta(hours=1),
    }
