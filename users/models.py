from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомный пользователь"""

    phone = models.CharField("Телефон", max_length=20, blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
