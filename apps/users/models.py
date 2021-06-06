from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework.authtoken.models import Token

from apps.utils.models import BaseModel


class User(BaseModel, AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    @property
    def token(self) -> str:
        token, _ = Token.objects.get_or_create(user=self)
        return token.key


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.creator and not self.users.filter(pk=self.creator.pk).exists():
            self.users.add(self.creator)


class UserInvitation(models.Model):
    email = models.EmailField()
