from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterByPhoneNumberSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=10, max_length=10, allow_null=False, required=True)


class CodeVerificationSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=10, max_length=10, allow_null=False, required=True)
    token = serializers.CharField(min_length=6, max_length=6, allow_null=False, required=True)


class CompleteUserInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=2, max_length=64, allow_null=True, required=True)
    last_name = serializers.CharField(min_length=2, max_length=64, allow_null=True, required=True)
    email = serializers.EmailField(min_length=2, max_length=64, allow_null=True, required=True)


class CompleteUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=4, max_length=256, allow_null=False, required=True)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=10, max_length=10, allow_null=False, required=True)
    password = serializers.CharField(min_length=4, max_length=256, allow_null=False, required=True)
