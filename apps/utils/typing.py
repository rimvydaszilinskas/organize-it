# noinspection PyUnresolvedReferences
from decimal import Decimal
import typing as t

if t.TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from apps.calendars.models import CalendarEvent, CalendarEventAttendee
    # noinspection PyUnresolvedReferences
    from apps.users.models import User, UserGroup
