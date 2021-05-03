from __future__ import annotations

from rest_framework import serializers

import apps.utils.typing as td

from .models import User, UserGroup


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

    class Meta:
        model = UserGroup
        fields = (
            'uuid',
            'name',
            'description',
            'creator',
            'users',
        )

    def create(self, validated_data):
        user = self.context['request'].user
        return self.Meta.model.objects.create(
            creator=user,
            **validated_data
        )


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
