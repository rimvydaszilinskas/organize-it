from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http.response import Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.settings import api_settings

from .models import User, UserGroup
from .permissions import UserGroupPermission
from .serializers import (
    UserAuthenticationSerializer,
    UserGroupSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class UserAuthenticationView(generics.CreateAPIView):
    serializer_class = UserAuthenticationSerializer
    permission_classes = []


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = []


class UserGroupsView(generics.ListCreateAPIView):
    serializer_class = UserGroupSerializer

    def get_queryset(self):
        return UserGroup.objects.filter(Q(creator=self.request.user) | Q(users=self.request.user)).distinct()


class UserGroupView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserGroupSerializer
    model = UserGroup
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + \
        [UserGroupPermission]

    def get_object(self):
        group = get_object_or_404(self.model, uuid=self.kwargs['uuid'])
        self.check_object_permissions(self.request, group)
        return group


class UserFilterView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(self._get_query()).exclude(pk=self.request.user.pk)

    def _get_query(self):
        lookup = self.request.query_params.get('lookup')
        query = Q()
        if lookup is not None:
            query = Q(email__icontains=lookup)

        group = self.request.query_params.get('group')
        if group:
            try:
                group = get_object_or_404(UserGroup, uuid=group)
                query &= Q(user_groups=group)
            except (UserGroup.DoesNotExist, ValidationError):
                raise Http404()
        return query


class SelfUserView(generics.RetrieveAPIView):
    serializer_class = UserAuthenticationSerializer

    def get_object(self):
        return self.request.user
