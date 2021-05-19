from __future__ import annotations

from django.shortcuts import get_object_or_404
from django.utils import timezone

from django_ical.views import ICalFeed

import apps.utils.typing as td
from .models import CalendarEvent, UserCalendar


class CalendarEventFeed(ICalFeed):
    product_id = '-//organize-it.com//v1/EN'
    file_name = 'feed.ics'
    timezone = 'UTC'

    def __call__(self, request, *args, **kwargs):
        self.request = request

        self.calendar = get_object_or_404(UserCalendar, uuid=kwargs['uuid'])
        self.now = timezone.now()
        self.user = self.calendar.user

        return super().__call__(request, *args, **kwargs)

    def items(self):
        events = CalendarEvent.objects.get_user_events(self.user).filter(
            time_start__gte=self.now).order_by('time_start')
        return events

    def item_guid(self, item: td.CalendarEvent):
        return f"{item.uuid.hex}@organizeit"

    def item_description(self, item: td.CalendarEvent):
        return item.description

    def item_start_datetime(self, item: td.CalendarEvent):
        return item.time_start

    def item_end_datetime(self, item: td.CalendarEvent):
        return item.time_end

    def item_link(self, item: td.CalendarEvent):
        return f"/calendars/events/{item.uuid.hex}"

    def item_title(self, item: td.CalendarEvent):
        return item.name
