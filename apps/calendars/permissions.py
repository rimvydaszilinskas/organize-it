from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS

import apps.utils.typing as td


class EventAttendeePermission(BasePermission):
    def has_object_permission(self, request, _, obj: td.CalendarEventAttendee) -> bool:
        conditions = [
            obj.user == request.user,
            obj.event.organizer == request.user,
        ]
        if request.method in SAFE_METHODS:
            conditions.append(
                obj.event.attendees.filter(user=request.user).exists()
            )
        return any(conditions)


class EventPermission(BasePermission):
    def has_object_permission(self, request, _, obj: td.CalendarEvent) -> bool:
        conditions = [
            obj.organizer == request.user,
        ]

        if request.method in SAFE_METHODS:
            conditions.append(obj.attendees.filter(user=request.user).exists())

        return any(conditions)
