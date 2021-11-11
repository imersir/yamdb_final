from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager


class APIUserManager(UserManager):

    def _create_user(self, username, email, password, **extra_fields):
        email = self.normalize_email(email)
        username = AbstractUser.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields['role'] = 'admin'
        return super().create_superuser(username=username, email=email,
                                        password=password, **extra_fields)
