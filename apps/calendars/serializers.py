import typing as t

from rest_framework import serializers

from apps.users.models import User
from apps.users.serializers import UserSerializer, UserGroupSerializer

from .models import CalendarEvent, CalendarEventAttendee


class CalendarEventAttendeeSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex', read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = CalendarEventAttendee
        fields = (
            'uuid',
            'email',
            'user',
            'response',
            'note'
        )


class CalendarEventSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex', read_only=True)
    attendees = CalendarEventAttendee(many=True, read_only=True)
    organizer = UserSerializer(read_only=True)
    group = UserGroupSerializer(read_only=True)
    emails = serializers.ListField(
        child=serializers.EmailField(), write_only=True
    )
    check = serializers.BooleanField(
        write_only=True, required=False, default=False)

    class Meta:
        model = CalendarEvent
        fields = (
            'uuid',
            'name',
            'description',
            'time_start',
            'time_end',
            'organizer',
            'group',
            'attendees',
            'emails',
        )

    def validate_emails(self, emails: t.List[str]):
        users = []

        for email in emails:
            try:
                user = User.objects.get(email=email)
                users.append(user)
            except User.DoesNotExist:
                users.append(email)

        return users
