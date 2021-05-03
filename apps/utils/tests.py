from django.test import TestCase

from apps.calendars.models import CalendarEvent, CalendarEventAttendee
from apps.users.factories import UserFactory, UserGroupFactory
import apps.utils.typing as td


class BaseTestCase(TestCase):
    def setUp(self):
        self.user: td.User = UserFactory()
        self.group: td.UserGroup = UserGroupFactory()
        self.group2: td.UserGroup = UserGroupFactory()

        self.group.users.add(self.users)

        users = UserFactory.create_batch(10)

        for user in users:
            self.group.users.add(user)

        users = UserFactory.create_batch(10)

        for user in users:
            self.group2.users.add(user)
