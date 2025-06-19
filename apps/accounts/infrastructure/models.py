from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.accounts.infrastructure import models


class User(AbstractUser):
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


# from documentation of django
"""from django.conf import settings
from django.db import models


class Article(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
"""
