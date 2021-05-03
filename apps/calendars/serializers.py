import typing as t

from rest_framework import serializers

from apps.users.models import User
from apps.users.serializers import UserSerializer, UserGroupSerializer

from .finders import EventTimeValidator
from .models import CalendarEvent, CalendarEventAttendee


class CalendarEventAttendeeSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex', read_only=True)
    user = UserSerializer(read_only=True)
    email = serializers.EmailField(read_only=True)

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
    attendees = CalendarEventAttendeeSerializer(many=True, read_only=True)
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
            'check',
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

    def validate(self, attrs):
        check = attrs.pop('check', False)
        if check:
            validator = EventTimeValidator(
                attrs['time_start'],
                attrs['time_end'],
                attrs['emails']
            )
            if not validator.validate():
                raise serializers.ValidationError(validator.errors)

        return attrs

    def create(self, validated_data):
        emails = validated_data.pop('emails')

        event = self.Meta.model.objects.create(
            organizer=self.context['request'].user, **validated_data)

        for email in emails:
            if isinstance(email, User):
                email = email.email
            CalendarEventAttendee.objects.create(
                email=email,
                event=event
            )

        return event
