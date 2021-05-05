from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.utils.tests import BaseTestCase, BaseAPITestCase

from .exceptions import EventTimeValidationError
from .models import CalendarEvent
from .validators import EventTimeValidator


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
