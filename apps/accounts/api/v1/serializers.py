from rest_framework import serializers
from rest_framework import exceptions
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterByPhoneNumberSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=10, max_length=10, allow_null=False, required=True)

    def validate_username(self, username):
        if not username.startswith('9'):
            raise exceptions.ValidationError(detail='PhoneNumber must be start with 9.')
        return username


class CodeVerificationSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=10, max_length=10, allow_null=False, required=True)
    token = serializers.CharField(min_length=6, max_length=6, allow_null=False, required=True)

    def validate_username(self, username):
        if not username.startswith('9'):
            raise exceptions.ValidationError(detail='PhoneNumber must be start with 9.')
        return username

    def validate_token(self, token):
        if not token.isdigit():
            raise exceptions.ValidationError(detail='Token must be digit numbers.')
        return token


class CompleteUserInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=2, max_length=64, allow_null=True, required=True)
    last_name = serializers.CharField(min_length=2, max_length=64, allow_null=True, required=True)
    email = serializers.EmailField(min_length=2, max_length=64, allow_null=True, required=True)


class CompleteUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=4, max_length=256, allow_null=False, required=True)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=10, max_length=10, allow_null=False, required=True)
    password = serializers.CharField(min_length=4, max_length=256, allow_null=False, required=True)

    def validate_username(self, username):
        if not username.startswith('9'):
            raise exceptions.ValidationError(detail='PhoneNumber must be start with 9.')
        return username
