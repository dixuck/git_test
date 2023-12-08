from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from applications.account.serializers import (
    NewUserSerializer, ChangePasswordSerializer, UserSerializer,
    ChangeForgottenPasswordSerializer, ActivationSerializer,
    DropPasswordSerializer
    )
from rest_framework.status import (
    HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_201_CREATED)
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


class NewUserView(CreateAPIView):
    serializer_class = NewUserSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'Сообщение': 'Аккаунт успешно создан'})

    def perform_create(self, serializer):
        serializer.save()


class ChangePasswordView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.set_new_password()
        return Response(
            {'message': 'password changed successfully'},
            status=HTTP_200_OK)


class UserView(APIView):
    def get(self, request,):
        try:
            user = User.objects.get(id=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response("User not found", status=404)


class ActivationView(CreateAPIView):
    serializer_class = ActivationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.activate()
        return Response(
            {'message': 'Account activated successfully'},
            status=HTTP_202_ACCEPTED)


class DropPasswordView(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Delete password",
        responses={200: DropPasswordSerializer()},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email'],
        ),
        )
    def post(self, request, *args, **kwargs):
        serializer = DropPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_activation_code()
        return Response(
            {'Message': 'Sended activation code'},
            status=HTTP_200_OK)


class ChangeForgottenPasswordView(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Set new password",
        responses={200: ChangeForgottenPasswordSerializer()},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING),
                'password_confirm': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['code', 'new_password', 'password_confirm'],
        ),
        )
    def post(self, request, *args, **kwargs):
        serializer = ChangeForgottenPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.set_new_password()
        return Response(
            {'message': 'Password changed successfully'},
            status=HTTP_201_CREATED)
