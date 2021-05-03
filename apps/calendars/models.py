from django.db import models

from apps.users.models import User
from apps.utils.models import BaseModel


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

    def save(self, *args, **kwargs):
        if self.user is None:
            try:
                self.user = User.objects.get(email=self.email)
            except User.DoesNotExist:
                pass
        return super().save(*args, **kwargs)
