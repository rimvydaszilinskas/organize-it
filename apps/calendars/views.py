from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.settings import api_settings

from .models import CalendarEvent, CalendarEventAttendee
from .permissions import EventAttendeePermission, EventPermission
from .serializers import CalendarEventAttendeeSerializer, CalendarEventSerializer, UserCalendarSerializer


class CalendarEventsView(generics.ListCreateAPIView):
    serializer_class = CalendarEventSerializer

    def get_queryset(self):
        return CalendarEvent.objects.get_user_events(self.request.user).order_by('-time_start')


class CalendarEventView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CalendarEventSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + \
        [EventPermission]

    def get_object(self):
        event = get_object_or_404(CalendarEvent, uuid=self.kwargs['uuid'])
        self.check_object_permissions(self.request, event)
        return event


class AttendanceView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CalendarEventAttendeeSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + \
        [EventAttendeePermission]

    def get_object(self):
        attendee = get_object_or_404(
            CalendarEventAttendee, uuid=self.kwargs['uuid'])
        self.check_object_permissions(self.request, attendee)
        return attendee


class UserCalendarsView(generics.ListCreateAPIView):
    serializer_class = UserCalendarSerializer

    def get_queryset(self):
        return self.request.user.calendars.all()


class UserCalendarView(generics.RetrieveDestroyAPIView):
    serializer_class = UserCalendarSerializer

    def get_object(self):
        return get_object_or_404(self.request.user.calendars, uuid=self.kwargs['uuid'])
