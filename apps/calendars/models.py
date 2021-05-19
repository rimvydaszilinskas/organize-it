from __future__ import annotations
import math
import typing as t

from email.mime.text import MIMEText
from ics import (
    Calendar as ICSCalendar,
    Event as ICSEvent,
    Organizer as ICSOrganizer,
    Attendee as ICSAttendee,
)

from django.db import models
from django.db.models import Q
from django.utils.text import slugify

from apps.users.models import User
from apps.utils.models import BaseModel
import apps.utils.typing as td

from .emails import send_invitations


class CalendarEventManager(models.Manager):
    def get_user_events(self, user: td.User) -> td.QuerySet:
        return self.filter(Q(organizer=user) | Q(attendees__user=user))

    def get_email_events(self, email: str) -> td.QuerySet:
        return self.filter(attendees__email=email)


class CalendarEvent(BaseModel):
    PRETTY_FORMAT = '%A, %d %B %Y, %H:%M'
    PRETTY_DATE_FORMAT = '%Y-%m-%d'
    PRETTY_TIME_FORMAT = '%H:%M'

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

    ics_uid_override = models.CharField(
        null=True,
        blank=True,
        max_length=255
    )

    objects = CalendarEventManager()

    def __str__(self) -> str:
        return f'{self.name} - event'

    @property
    def pretty_start(self) -> str:
        return self.time_start.strftime(self.PRETTY_FORMAT)

    @property
    def pretty_end(self) -> str:
        return self.time_end.strftime(self.PRETTY_FORMAT)

    @property
    def pretty_start_date(self) -> str:
        return self.time_start.strftime(self.PRETTY_DATE_FORMAT)

    @property
    def pretty_end_date(self) -> str:
        return self.time_end.strftime(self.PRETTY_DATE_FORMAT)

    @property
    def pretty_start_time(self) -> str:
        return self.time_start.strftime(self.PRETTY_TIME_FORMAT)

    @property
    def pretty_end_time(self) -> str:
        return self.time_end.strftime(self.PRETTY_TIME_FORMAT)

    @property
    def length(self):
        return math.floor((self.time_end - self.time_start).seconds / 60)

    @property
    def ics_uid(self) -> str:
        if self.ics_uid_override and len(self.ics_uid_override):
            return self.ics_uid_override
        return f'{self.uuid}@organize-it'

    def get_ics_event(self) -> ICSEvent:
        event = ICSEvent(
            name=self.name,
            begin=self.time_start,
            end=self.time_end,
            description=self.description,
            uid=self.ics_uid
        )

        for attendee in self.attendees.all():
            data = {
                'email': attendee.email
            }
            if attendee.user:
                data.update({
                    'common_name': attendee.user.get_full_name()
                })

            event.attendees.add(ICSAttendee(**data))

        if self.organizer:
            event.organizer = ICSOrganizer(
                email=self.organizer.email,
                common_name=self.organizer.get_full_name()
            )

        return event

    def get_ics_calendar(self) -> ICSCalendar:
        calendar = ICSCalendar()
        calendar.events.add(self.get_ics_event())
        return calendar

    def get_ics_string(self) -> str:
        return str(self.get_ics_calendar())

    def get_as_email_attachment(self) -> MIMEText:
        mime = MIMEText(self.get_ics_string())
        name = slugify(self.name)
        filename = f'{name}-organizeit.ics'
        mime.add_header('Filename', filename)
        mime.add_header('Content-Disposition',
                        f'attachment; filename={filename}')
        return mime

    def send(self):
        send_invitations(self)


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


class UserCalendar(BaseModel):
    name = models.CharField(null=True, blank=True, max_length=25)

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='calendars',
    )

    def __str__(self) -> str:
        return f"{self.user} calendar{(' ' + self.name) if self.name else ''}"
