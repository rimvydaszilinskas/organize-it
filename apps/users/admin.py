from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, UserGroup


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    pass


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    readonly_fields = (
        'uuid',
    )

    autocomplete_fields = (
        'creator',
        'users',
    )
