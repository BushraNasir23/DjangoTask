from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'password', 'role']
        read_only_fields = ['id', ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user_profile = UserProfile(**validated_data)
        user_profile.set_password(password)
        user_profile.save()
        return user_profile


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({
                "username": f"The username `{username}` does not exist. Please check and try again."
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "is_active": "This account is inactive. Please contact support for assistance."
            })

        if not check_password(password, user.password):
            raise serializers.ValidationError({
                "password": "The password you entered is incorrect. Please try again."
            })
        return super().validate(attrs)

    class Meta:
        fields = ['username', 'password']


class TokenRevokeSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255, required=True)

    def create(self, validated_data):
        refresh_token = validated_data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return TokenRevokeSerializer()
