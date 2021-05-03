from django.contrib import admin

from .models import CalendarEvent, CalendarEventAttendee


class CalendarEventAttendeeInline(admin.TabularInline):
    model = CalendarEventAttendee
    extra = 0

    autocomplete_fields = (
        'user',
    )


@admin.register(CalendarEvent)
class CalendarEvent(admin.ModelAdmin):
    inlines = (
        CalendarEventAttendeeInline,
    )

    autocomplete_fields = (
        'organizer',
    )
