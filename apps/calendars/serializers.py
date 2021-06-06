import typing as t

from rest_framework import serializers

from apps.users.models import User, UserGroup
from apps.users.serializers import UserSerializer, UserGroupSerializer
import apps.utils.typing as td

from .validators import EventTimeValidator
from .models import CalendarEvent, CalendarEventAttendee, UserCalendar


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
    group_uuid = serializers.UUIDField(format='hex', required=False)
    emails = serializers.ListField(
        child=serializers.EmailField(), write_only=True, required=False
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
            'group_uuid',
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

    def validate_group_uuid(self, uuid):
        try:
            return UserGroup.objects.get(uuid=uuid)
        except UserGroup.DoesNotExist:
            raise serializers.ValidationError('User Group does not exist')

    def validate(self, attrs):
        check = attrs.pop('check', False)

        if 'emails' in attrs:
            emails = attrs['emails']
        elif 'group_uuid' in attrs:
            emails = attrs['group_uuid'].users.all()
        else:
            raise serializers.ValidationError(
                'neither emails nor group_uuid exists in request')

        if attrs['time_start'] >= attrs['time_end']:
            raise serializers.ValidationError({
                'time_start': 'time_start must be smaller than time_end',
                'time_end': 'time_start must be smaller than time_end'
            })

        if (attrs['time_end'] - attrs['time_start']).seconds < 900:
            raise serializers.ValidationError(
                {'duration': 'Cannot create event shorter than 15 minutes'})

        if check:
            validator = EventTimeValidator(
                attrs['time_start'],
                attrs['time_end'],
                emails,
            )
            if not validator.validate():
                raise serializers.ValidationError(validator.errors)

        return attrs

    def create(self, validated_data):
        emails = validated_data.pop('emails', [])

        if 'group_uuid' in validated_data:
            group = validated_data.pop('group_uuid')
            validated_data.update({
                'group': group,
            })
            emails = group.users.values_list("email", flat=True)

        event: td.CalendarEvent = self.Meta.model.objects.create(
            organizer=self.context['request'].user, **validated_data)

        for email in emails:
            if isinstance(email, User):
                email = email.email
            CalendarEventAttendee.objects.create(
                email=email,
                event=event
            )

        event.send()

        return event


class UserCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCalendar
        fields = (
            'name',
        )

    def create(self, validated_data):
        return UserCalendar.objects.create(user=self.context['request'].user, **validated_data)
