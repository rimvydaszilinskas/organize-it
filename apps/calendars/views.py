from rest_framework import generics, status
from rest_framework.response import Response

from .models import CalendarEvent
from .serializers import CalendarEventAttendeeSerializer, CalendarEventSerializer


class CalendarEventsView(generics.ListCreateAPIView):
    serializer_class = CalendarEventSerializer

    def get_queryset(self):
        pass
