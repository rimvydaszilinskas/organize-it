from __future__ import annotations

import typing as t
from django.test import TestCase

from rest_framework.test import APIClient

from apps.users.factories import UserFactory, UserGroupFactory
import apps.utils.typing as td


class BaseTestCase(TestCase):
    def setUp(self):
        self.user: td.User = UserFactory()
        self.group: td.UserGroup = UserGroupFactory()
        self.group2: td.UserGroup = UserGroupFactory()

        self.group.users.add(self.user)

        users = UserFactory.create_batch(10)

        for user in users:
            self.group.users.add(user)

        users = UserFactory.create_batch(10)

        for user in users:
            self.group2.users.add(user)


class BaseAPITestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def authenticate_client(self, user: t.Optional[td.User] = None):
        if user is None:
            user = self.user
        self.client.force_login(user)
