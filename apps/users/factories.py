import factory
from factory.django import DjangoModelFactory

from .models import User, UserGroup


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda i: f'user-{i}')
    email = factory.Sequence(lambda i: f'user-{i}@testmail.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class UserGroupFactory(DjangoModelFactory):
    class Meta:
        model = UserGroup

    name = factory.Faker('sentence', nb_words=4)
