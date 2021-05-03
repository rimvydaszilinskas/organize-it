from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS

import apps.utils.typing as td


class UserGroupPermission(BasePermission):
    def has_object_permission(self, request, _, obj: td.UserGroup) -> bool:
        if request.method in SAFE_METHODS:
            return request.user in obj.users.all()
        return request.user == obj.creator
