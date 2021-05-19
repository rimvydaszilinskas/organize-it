# noinspection PyUnresolvedReferences
from decimal import Decimal
import typing as t
from django.db.models import QuerySet

if t.TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from apps.calendars.models import CalendarEvent, CalendarEventAttendee, UserCalendar
    # noinspection PyUnresolvedReferences
    from apps.users.models import User, UserGroup
