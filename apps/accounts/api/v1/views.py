from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.api.v1.serializers import CodeVerificationSerializer
from apps.accounts.api.v1.serializers import RegisterByPhoneNumberSerializer
from apps.accounts.api.v1.serializers import CompleteUserInfoSerializer
from apps.accounts.api.v1.serializers import CompleteUserPasswordSerializer
from apps.accounts.api.v1.serializers import UserLoginSerializer
from utils.redis_handlers import check_user_token
from utils.redis_handlers import get_user_wait_time_token
from utils.redis_handlers import set_user_token
from utils.redis_handlers import increase_attemption
from utils.redis_handlers import remove_ip_from_redis
from utils.redis_handlers import remove_token_user
from utils.redis_handlers import is_blocking_ip


def get_ip_address(request) -> str:
    return x_forwarded_for.split(',')[0] if (
        x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR')) else request.META.get('REMOTE_ADDR')


class RegisterByPhoneNumber(APIView):
    model = get_user_model()
    serializer = RegisterByPhoneNumberSerializer

    def post(self, request):
        serialized_data = self.serializer(data=request.data)

        if not serialized_data.is_valid(raise_exception=True):
            return Response(data=serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

        if wait_time := get_user_wait_time_token(serialized_data.validated_data['username']):
            return Response(
                data={'message': f'{wait_time} second(s) left to get new token'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        if self.model.objects.filter(username=serialized_data.validated_data['username']).exists():
            return Response(data=serialized_data.validated_data, status=status.HTTP_200_OK)

        print(set_user_token(serialized_data.validated_data['username']))
        return Response(data=serialized_data.validated_data, status=status.HTTP_201_CREATED)


class VerifyCode(APIView):
    model = get_user_model()
    serializer = CodeVerificationSerializer

    def post(self, request):
        ip = get_ip_address(request)
        serialized_data = self.serializer(data=request.data)

        if wait_time := is_blocking_ip(ip):
            return Response(
                data={'message': f'After {wait_time} second(s) can try again.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        if not serialized_data.is_valid(raise_exception=True):
            return Response(data=serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

        if not check_user_token(serialized_data.validated_data['username'], serialized_data.validated_data['token']):
            if (try_count := increase_attemption(ip)) > 3:
                return Response(
                    data={'message': f'After {try_count} second(s) can try again.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            return Response(
                data={'message': f'Username or Token is not correct. {try_count} left to try again.'},
                status=status.HTTP_404_NOT_FOUND
            )
        user = self.model(username=serialized_data.validated_data['username'])
        user.save()
        remove_token_user(serialized_data.validated_data['username'])
        refresh = RefreshToken.for_user(user)
        remove_ip_from_redis(ip)
        return Response(
            data={'refresh': str(refresh), 'access': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )


class CompleteUserInfo(APIView):
    model = get_user_model()
    serializer = CompleteUserInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serialized_data = self.serializer(data=request.data)

        if not serialized_data.is_valid(raise_exception=True):
            return Response(data=serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

        if not (user := self.model.objects.filter(username=request.user.username).first()):
            return Response(data={'message': 'User does not exists'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user.email = serialized_data.validated_data['email']
        except IntegrityError as e:
            return Response(
                data={'message': f'{e}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.first_name = serialized_data.validated_data['first_name']
        user.last_name = serialized_data.validated_data['last_name']
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompleteUserPassword(APIView):
    model = get_user_model()
    serializer = CompleteUserPasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serialized_data = self.serializer(data=request.data)

        if not serialized_data.is_valid(raise_exception=True):
            return Response(data=serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

        if not (user := self.model.objects.filter(username=request.user.username).first()):
            return Response(data={'message': 'User does not exists'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(serialized_data.validated_data['password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginUser(APIView):
    model = get_user_model()
    serializer = UserLoginSerializer

    def post(self, request):
        ip = get_ip_address(request)
        serialized_data = self.serializer(data=request.data)

        if wait_time := is_blocking_ip(ip):
            return Response(
                data={'message': f'After {wait_time} second(s) can try again.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        if not serialized_data.is_valid(raise_exception=True):
            return Response(data=serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

        if not (user := authenticate(request, **serialized_data.validated_data)):
            if (try_count := increase_attemption(ip)) > 3:
                return Response(
                    data={'message': f'After {try_count} second(s) can try again.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            return Response(
                data={'message': f'Invalid credentials. {try_count} left to try again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        remove_ip_from_redis(ip)
        return Response(
            data={'refresh': str(refresh), 'access': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )
