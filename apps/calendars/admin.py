from django.contrib import admin

from .models import CalendarEvent, CalendarEventAttendee, UserCalendar


class CalendarEventAttendeeInline(admin.TabularInline):
    model = CalendarEventAttendee
    extra = 0

    autocomplete_fields = (
        'user',
    )


class UserCalendarInline(admin.TabularInline):
    model = UserCalendar
    extra = 0

    readonly_fields = (
        "uuid",
    )


@admin.register(CalendarEvent)
class CalendarEvent(admin.ModelAdmin):
    inlines = (
        CalendarEventAttendeeInline,
    )

    autocomplete_fields = (
        'organizer',
    )
