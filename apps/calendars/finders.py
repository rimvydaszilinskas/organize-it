from __future__ import annotations
from decimal import Decimal
import typing as t

from django.db.models import Q

from apps.users.models import User
import apps.utils.typing as td

from .exceptions import EventTimeValidationError
from .models import CalendarEvent


class EventTimeValidator(object):
    def __init__(self, start_time: Decimal, end_time: Decimal, users: t.Iterable[td.User]):
        self.start_time = start_time
        self.end_time = end_time
        self.users = users
        self.__errors = None

    def validate(self):
        self.__errors = {}
        for user in self.users:
            if not isinstance(user, User):
                continue
            events = CalendarEvent.objects.get_user_events(user).filter(self.__time_query)  # noqa
            if events.exists():
                self.__errors.update(
                    {user.email: 'User has an event at the given time slot'})

        return not bool(self.__errors)

    @property
    def errors(self):
        if self.__errors is None:
            raise EventTimeValidationError('.solve() needs to be run first')
        return self.__errors

    @property
    def __time_query(self):
        # check if starting time is in the event
        query = Q(time_start__lte=self.start_time, time_end__gte=self.start_time)  # noqa
        # check if ending time is in the event brackets
        query |= Q(time_start__lte=self.end_time, time_end__gte=self.end_time)  # noqa
        # Check if the whole event is inse the time brackets
        query |= Q(time_start__gte=self.start_time, time_end__lte=self.end_time)  # noqa
        return query
