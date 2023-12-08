from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class Role(models.TextChoices):
    doctor = 'Доктор'
    admin = 'Администратор'
    null = None


class UserManager(BaseUserManager):

    def _create(self, username, password, email, **extra_info):
        if not username:
            raise ValueError('Enter username')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_info)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, password, email, **extra_info):
        extra_info.setdefault('is_active', True)
        extra_info.setdefault('is_staff', False)
        return self._create(username, password, email, **extra_info)

    def create_superuser(self, username, password, email, **extra_info):
        extra_info.setdefault('is_active', True)
        extra_info.setdefault('is_staff', True)
        extra_info.setdefault('role', 'Администратор')
        return self._create(username, password, email,  **extra_info)


class User(AbstractBaseUser):
    username = models.CharField(max_length=24, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(
        max_length=13, choices=Role.choices, default=Role.null
        )
    is_authenticated = models.BooleanField(default=True)
    activation_code = models.CharField(max_length=10, blank=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def has_module_perms(self, app_label):
        return self.role == 'Администратор'

    def has_perm(self, obj=None):
        return self.role == 'Администратор'
