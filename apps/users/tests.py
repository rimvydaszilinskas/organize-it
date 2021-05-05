from django.urls import reverse

from apps.utils.tests import BaseAPITestCase

from .models import User, UserGroup


class TestUserFilterView(BaseAPITestCase):
    view_name = reverse('users:users')

    def test_search(self):
        self.authenticate_client()

        response = self.client.get(f'{self.view_name}?lookup=user')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), User.objects.count() - 1)

    def test_search_one(self):
        self.authenticate_client()

        response = self.client.get(
            f'{self.view_name}?lookup={User.objects.last().email}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_search_self(self):
        self.authenticate_client()

        response = self.client.get(
            f'{self.view_name}?lookup={self.user.email}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_search_group(self):
        self.authenticate_client()

        response = self.client.get(
            f'{self.view_name}?group={self.group.uuid.hex}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), self.group.users.count() - 1)

    def test_search_not_in_group_email(self):
        user = self.group.users.exclude(pk=self.user.pk).first()
        self.authenticate_client()

        response = self.client.get(
            f'{self.view_name}?group={self.group2.uuid.hex}&lookup={user.email}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


class TestUserGroupsView(BaseAPITestCase):
    view_name = reverse('users:user-groups')

    def test_create_group(self):
        self.authenticate_client()
        data = {
            'name': 'super name',
            'description': 'super description',
        }
        response = self.client.post(self.view_name, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        group = UserGroup.objects.get(uuid=response.data['uuid'])
        self.assertEqual(group.name, data['name'])
        self.assertEqual(group.description, data['description'])
        self.assertEqual(group.creator, self.user)

    def test_get_groups(self):
        self.authenticate_client()

        response = self.client.get(self.view_name)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class TestUserGroupView(BaseAPITestCase):
    view_name = 'users:user-group'

    def test_get_not_in_group(self):
        self.authenticate_client()

        response = self.client.get(
            reverse(self.view_name, args=[self.group2.uuid.hex]))

        self.assertEqual(response.status_code, 403)

    def test_get_group(self):
        self.authenticate_client()

        response = self.client.get(
            reverse(self.view_name, args=[self.group.uuid.hex]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['uuid'], self.group.uuid.hex)

    def test_update_group(self):
        self.authenticate_client()
        data = {
            'name': 'new name'
        }

        self.group.creator = self.user
        self.group.save()

        response = self.client.patch(
            reverse(self.view_name, args=[self.group.uuid.hex]), data=data, format='json')

        self.assertEqual(response.status_code, 200)

        self.group.refresh_from_db()

        self.assertEqual(self.group.name, 'new name')

    def test_update_group_not_creator(self):
        self.authenticate_client()

        response = self.client.patch(
            reverse(self.view_name, args=[self.group.uuid.hex]))

        self.assertEqual(response.status_code, 403)

    def test_delete_group(self):
        self.authenticate_client()

        self.group.creator = self.user
        self.group.save()

        response = self.client.delete(
            reverse(self.view_name, args=[self.group.uuid.hex]))

        self.assertTrue(response.status_code, 204)
        self.assertRaises(UserGroup.DoesNotExist,
                          UserGroup.objects.get, pk=self.group.pk)


class TestUserAuthenticationView(BaseAPITestCase):
    view_name = 'users:login'

    def setUp(self):
        super().setUp()
        self.user.set_password('password')
        self.user.save()

    def test_login(self):
        response = self.client.post(reverse(self.view_name), data={
            'email': self.user.email,
            'password': 'password'
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user.token, response.data['token'])

    def test_bad_login(self):
        response = self.client.post(reverse(self.view_name), data={
            'email': self.user.email,
            'password': 'bad password'
        })

        self.assertEqual(response.status_code, 400)


class TestUserRegistrationView(BaseAPITestCase):
    view_name = 'users:registration'

    def test_user_registration(self):
        response = self.client.post(reverse(self.view_name), data={
            'email': 'notusedemail@meila.com',
            'username': 'superunique',
            'password': 'notsocoll',
        })

        self.assertEqual(response.status_code, 201)
        uuid = response.data.get('uuid')
        self.assertIsNotNone(uuid)
        user = User.objects.get(uuid=uuid)

        self.assertEqual(user.email, 'notusedemail@meila.com')
        self.assertEqual(user.username, 'superunique')

    def test_used_email(self):
        response = self.client.post(reverse(self.view_name), data={
            'email': self.user.email,
            'username': self.user.username,
            'password': 'socooool'
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
        self.assertIn('username', response.data)
