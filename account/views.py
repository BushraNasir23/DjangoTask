from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError

from .auth import get_tokens_for_user
from .models import EmailCode, UserProfile
from .serializers import (
    UserRegistrationSerializer,
    TokenRevokeSerializer,
    UserLoginSerializer
)


class RegisterView(CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer


class UserLogin(CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({
                "errors": serializer.errors
            })
        username = serializer.validated_data.get("username")
        user = UserProfile.objects.get(username=username, is_active=True)
        return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TokenRevokeSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except TokenError:
            return Response({
                "detail": "Token is blacklisted",
                "code": "token_not_valid"
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_200_OK)


class VerifySignupEmail(APIView):

    def get(self, *args, email: str, code: str):
        user_profile = UserProfile.objects.filter(
            email=email
        ).first()
        if not user_profile:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        email_code = EmailCode.objects.filter(
            profile=user_profile,
            mail_code=code,
            is_active=True,
        ).first()
        if email_code:
            user_profile.is_active = True
            user_profile.save()
            email_code.is_active = False
            email_code.save()
        return Response(status=status.HTTP_200_OK)
