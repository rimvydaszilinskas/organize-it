from __future__ import annotations

import typing as t

from django.db import models
from django.db.models import Q

from apps.users.models import User
from apps.utils.models import BaseModel
import apps.utils.typing as td


class CalendarEventManager(models.Manager):
    def get_user_events(self, user: td.User) -> td.QuerySet:
        return self.filter(Q(organizer=user) | Q(attendees__user=user))

    def get_email_events(self, email: str) -> td.QuerySet:
        return self.filter(attendees__email=email)


class CalendarEvent(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(
        null=True,
        blank=True
    )
    organizer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        'users.UserGroup',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()

    objects = CalendarEventManager()

    def __str__(self) -> str:
        return f'{self.name} - event'


class CalendarEventAttendee(BaseModel):
    RESPONSES = (
        ('y', 'Yes'),
        ('n', 'No'),
        ('m', 'Maybe'),
        ('u', 'undefined'),
    )
    event = models.ForeignKey(
        CalendarEvent,
        on_delete=models.CASCADE,
        related_name='attendees',
    )
    email = models.EmailField()
    user = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='attendances'
    )
    response = models.CharField(
        max_length=1,
        choices=RESPONSES,
        default='u'
    )
    note = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        return f'{self.event} attendee {self.email}'

    def save(self, *args, **kwargs) -> t.NoReturn:
        if self.user is None:
            try:
                self.user = User.objects.get(email=self.email)
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)
