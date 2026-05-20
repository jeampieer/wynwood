from django.contrib.auth.models import AbstractUser
from django.db import models

from applications.accounts.managers import UserManager


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.email
