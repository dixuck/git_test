from rest_framework import serializers, status
from django.contrib.auth import get_user_model, password_validation
from applications.services.models import Doctor, Service
from django.core.validators import RegexValidator
from applications.account.tasks import (
    send_activation_code_task, send_drop_password_code_task)
from applications.account.utils import create_activation_code


User = get_user_model()
phone_regex = RegexValidator(
    regex=r'^(\+\d{1,3}|0)\d{10,15}$',
    message="Phone number must be entered in the format:" +
    " '+999999999' or '0999999999'. Up to 15 digits allowed.")

User = get_user_model()


class NewUserSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(
        max_length=200, write_only=True)
    name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    phone_number = serializers.CharField(
        validators=[phone_regex], max_length=15, required=False
        )
    profession = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'password', 'password_confirmation',
            'role', 'name', 'last_name', 'phone_number', 'profession', 'email')
        extra_kwargs = {
            'password': {'write_only': True},

        }

    def validate_password(self, password):
        password_validation.validate_password(
            password, self.Meta.model)
        return password

    def validate(self, attrs: dict):
        password = attrs.get('password')
        password_confirmation = attrs.pop('password_confirmation')
        if password != password_confirmation:
            raise serializers.ValidationError(
                {'message': 'Пароли должны совпадать'},
                code=status.HTTP_400_BAD_REQUEST)
        role = attrs.get('role')
        name = attrs.get('name')
        last_name = attrs.get('last_name')
        phone_number = attrs.get('phone_number')
        profession = attrs.get('profession')
        if role == 'Доктор':
            if not name or not last_name or not phone_number or not profession:
                raise serializers.ValidationError(
                    {'message': 'Поля name, last_name,\
                    phone_number, profession обязательны для роли "Доктор"'},
                    code=status.HTTP_400_BAD_REQUEST
                )
        return attrs

    def create(self, validated_data):

        name = validated_data.pop('name', None)
        last_name = validated_data.pop('last_name', None)
        phone_number = validated_data.pop('phone_number', None)
        profession = validated_data.pop('profession', None)
        description = validated_data.pop('description', 'blank')
        schedule = validated_data.pop('schedule', 'blank')
        user = User.objects.create_user(**validated_data)
        if user.role == 'Доктор':
            doctor = Doctor.objects.create(
                user=user, name=name, last_name=last_name,
                phone_number=phone_number, profession=profession,
                description=description, schedule=schedule
                )
            service = Service.objects.get(pk=1)
            doctor.services.add(service)
        user_id = user.id
        create_activation_code(user)
        send_activation_code_task.delay(user_id)

        return user


class ChangePasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    password_confirm = serializers.CharField(max_length=128)

    def validate_current_password(self, current_password):
        user = self.context.get('request').user
        if user.check_password(current_password):
            return current_password
        raise serializers.ValidationError('Wrong password')

    def validate(self, attrs):
        new_pass = attrs.get('new_password')
        pass_confirm = attrs.get('password_confirm')
        if new_pass != pass_confirm:
            raise serializers.ValidationError('Passwords do not match')

        return attrs

    def set_new_password(self):
        new_password = self.validated_data.get('new_password')
        user = self.context.get('request').user
        user.set_password(new_password)
        user.save()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class ActivationSerializer(serializers.Serializer):
    activation_code = serializers.CharField(max_length=10)

    def validate_activation_code(self, activation_code):
        code_exists = User.objects.filter(
            activation_code=activation_code).exists()

        if code_exists:
            return activation_code
        raise serializers.ValidationError(
            {'message': 'activation code does not match'},
            code=status.HTTP_400_BAD_REQUEST)

    def activate(self):
        code = self.validated_data.get('activation_code')
        user = User.objects.get(activation_code=code)
        user.is_active = True
        user.activation_code = ''
        user.save()


class DropPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=255)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'User with this email does not exist'
                )
        return email

    def send_activation_code(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        create_activation_code(user)
        send_drop_password_code_task.delay(email, user.activation_code)


class ChangeForgottenPasswordSerializer(serializers.Serializer):

    code = serializers.CharField(max_length=10)
    new_password = serializers.CharField(max_length=128)
    password_confirm = serializers.CharField(max_length=128)

    def validate_code(self, code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError({'message': 'Wrong code'})
        return code

    def validate(self, attrs):
        new_pass = attrs.get('new_password')
        pass_confirm = attrs.get('password_confirm')
        if new_pass != pass_confirm:
            raise serializers.ValidationError(
                {'message': 'Passwords do not match'})

        return attrs

    def set_new_password(self):
        code = self._validated_data.get('code')
        new_password = self.validated_data.get('new_password')
        user = User.objects.get(activation_code=code)
        user.set_password(new_password)
        user.activation_code = ''
        user.save()
