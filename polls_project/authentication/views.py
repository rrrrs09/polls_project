from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer

User = get_user_model()


class UserCreateView(GenericAPIView):
    """Регистрация пользователя"""
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User(username=serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()

        users_group = Group.objects.get(name='users')
        users_group.user_set.add(user)
        token = Token.objects.create(user=user)

        data = {'token': token.key}
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    """Аутентификация пользователя"""
    serializer_class = UserSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            data = {'token': token.key}
            return Response(data)
        msg = 'Неверный логин или пароль'
        return Response(data={'error': msg}, status=400)


class LogoutView(APIView):
    """Выход из системы"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
