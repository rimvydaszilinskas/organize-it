from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework.authtoken.models import Token

from apps.utils.models import BaseModel


class User(BaseModel, AbstractUser):
    @property
    def token(self) -> str:
        return Token.objects.get_or_create(user=self).key


class UserGroup(BaseModel, models.Model):
    creator = models.ForeignKey(
        User,
        related_name='created_groups',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    users = models.ManyToManyField(
        User,
        related_name='user_groups'
    )
    name = models.CharField(max_length=30)
    description = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        return f'{self.name} - user group'
