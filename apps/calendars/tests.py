from datetime import timedelta

from django.utils import timezone
from django.urls import reverse

from apps.utils.tests import BaseTestCase, BaseAPITestCase

from .exceptions import EventTimeValidationError
from .models import CalendarEvent
from .validators import EventTimeValidator

FORMAT = '%Y-%m-%dT%H:%M'


class TimeValidatorTest(BaseTestCase):
    def test_user_busy(self):
        user = self.group.users.first()
        start_date = timezone.now()
        CalendarEvent.objects.create(
            name='Busy',
            organizer=user,
            time_start=start_date,
            time_end=start_date + timedelta(hours=1)
        )

        validator = EventTimeValidator(
            timezone.now() - timedelta(hours=1),
            timezone.now() + timedelta(hours=1),
            self.group.users.all()
        )

        self.assertRaises(EventTimeValidationError, validator.get_errors)
        self.assertFalse(validator.validate())

        errors = validator.errors

        self.assertIn(user.email, errors)


class CalendarEventsView(BaseAPITestCase):
    view_name = reverse('calendars:user-events-view')

    def setUp(self):
        super().setUp()
        self.authenticate_client()

    def test_create_event(self):
        self.authenticate_client()
        start = timezone.now() + timedelta(days=10)
        end = start + timedelta(hours=3)
        user1 = self.group.users.exclude(pk=self.user.pk).first()
        email1 = user1.email
        email2 = 'nonexisting@mail.com'

        data = {
            'name': 'Testing event',
            'description': 'Cool description',
            'time_start': start.strftime(FORMAT),
            'time_end': end.strftime(FORMAT),
            'emails': [
                email1,
                email2,
            ]
        }

        response = self.client.post(self.view_name, data=data, format='json')

        self.assertEqual(response.status_code, 201)

        event = CalendarEvent.objects.get(uuid=response.data['uuid'])

        self.assertEqual(data['name'], event.name)
        self.assertEqual(data['description'], event.description)
        self.assertEqual(event.attendees.count(), 2)
        self.assertEqual(event.organizer, self.user)

        self.assertEqual(end.strftime(FORMAT), event.time_end.strftime(FORMAT))
        self.assertEqual(
            start.strftime(FORMAT),
            event.time_start.strftime(FORMAT)
        )

        attendee = event.attendees.get(email=email1)

        self.assertEqual(attendee.response, 'u')
        self.assertIsNotNone(attendee.user)
        self.assertEqual(attendee.user, user1)

        attendee = event.attendees.get(email=email2)

        self.assertEqual(attendee.response, 'u')
        self.assertIsNone(attendee.user)

    def test_short_event(self):
        self.authenticate_client()
        start = timezone.now() + timedelta(days=10)
        end = start + timedelta(minutes=10)
        user1 = self.group.users.exclude(pk=self.user.pk).first()
        email1 = user1.email
        data = {
            'name': 'Testing event',
            'description': 'Cool description',
            'time_start': start.strftime(FORMAT),
            'time_end': end.strftime(FORMAT),
            'emails': [
                email1,
            ]
        }

        response = self.client.post(self.view_name, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('duration', response.data)

    def test_end_before_start(self):
        self.authenticate_client()
        start = timezone.now() + timedelta(days=10)
        end = start - timedelta(minutes=10)
        user1 = self.group.users.exclude(pk=self.user.pk).first()
        email1 = user1.email
        data = {
            'name': 'Testing event',
            'description': 'Cool description',
            'time_start': start.strftime(FORMAT),
            'time_end': end.strftime(FORMAT),
            'emails': [
                email1,
            ]
        }

        response = self.client.post(self.view_name, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('time_start', response.data)
        self.assertIn('time_end', response.data)
