from __future__ import annotations
import typing as t

from django.conf import settings
from rest_framework import serializers

from apps.calendars.emails import send_user_invitations
import apps.utils.typing as td

from .models import User, UserGroup, UserInvitation


class UserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex', read_only=True)

    class Meta:
        model = User
        fields = (
            'uuid',
            'username',
            'email',
            'first_name',
            'last_name',
        )


class UserGroupSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex', read_only=True)
    creator = UserSerializer(read_only=True)
    users = UserSerializer(many=True, read_only=True)
    emails = serializers.ListField(
        child=serializers.EmailField(), write_only=True
    )

    class Meta:
        model = UserGroup
        fields = (
            'uuid',
            'name',
            'description',
            'creator',
            'users',
            'emails',
        )

    @staticmethod
    def validate_emails(emails: t.List[str]) -> t.Iterable[td.User]:
        users = []

        for email in emails:
            try:
                users.append(User.objects.get(email=email))
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    f'User with email {email} is not registered in the system')

        return users

    def create(self, validated_data):
        user = self.context['request'].user
        users = validated_data.pop('emails')

        group: td.UserGroup = self.Meta.model.objects.create(
            creator=user,
            **validated_data
        )

        for member in users:
            group.users.add(member)
        return group


class UserAuthenticationSerializer(UserSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    token = serializers.SerializerMethodField()
    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'token',
            'password',
        )

    def get_token(self, obj: td.User):
        return obj.token

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']
        msg = 'User does not exist/incorrect password'

        try:
            self.instance: td.User = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(msg)

        if not self.instance.check_password(password):
            raise serializers.ValidationError(msg)

        return attrs

    def create(self, _):
        raise NotImplementedError()

    def update(self, instance, _):
        return instance


class UserRegistrationSerializer(UserSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + (
            'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user: td.User = User.objects.create(**validated_data)
        user.set_password(password)
        user.save(update_fields=['password'])
        return user


class UserInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInvitation
        fields = (
            'email',
        )

    @staticmethod
    def validate_email(email):
        if User.objects.filter(email=email).exists() or UserInvitation.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                f'Invitation or user for email {email} already exists')
        return email

    def create(self, validated_data):
        instance: td.UserInvitation = super().create(validated_data)

        if not settings.TESTING:
            send_user_invitations.delay(instance.email)
        return instance


class PasswordChangeSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(max_length=100, write_only=True)
    new_password = serializers.CharField(
        max_length=100, min_length=5, write_only=True)

    class Meta:
        model = User
        fields = (
            'current_password',
            'new_password',
        )

    def validate_current_password(self, password):
        user: td.User = self.instance

        if not user.check_password(password):
            raise serializers.ValidationError('is not valid')

        return password

    def validate(self, attrs):
        if attrs['current_password'] == attrs['new_password']:
            raise serializers.ValidationError('Passwords cannot match')
        return attrs

    def update(self, instance: td.User, validated_data):
        password = validated_data['new_password']
        instance.set_password(password)
        instance.save(update_fields=['password'])
        return instance
