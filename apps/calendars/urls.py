from django.conf.urls import url

from . import views, feeds

urlpatterns = [
    url(r'^events/$', views.CalendarEventsView.as_view(), name='user-events-view'),
    url(r'^events/(?P<uuid>[0-9a-f]{32})/$',
        views.CalendarEventView.as_view(), name='event'),
    url(r'^events/attendees/(?P<uuid>[0-9a-f]{32})/$',
        views.AttendanceView.as_view(), name='attendance'),
    url(r'^feeds/$', views.UserCalendarsView.as_view(), name='user-feeds'),
    url(r'^feeds/(?P<uuid>[0-9a-f]{32})/$',
        views.UserCalendarView.as_view(), name='user-feed-view'),

    url(r'^(?P<uuid>[0-9a-f]{32})/feed.ics$',
        feeds.CalendarEventFeed(), name='user-calendar-feed'),
]
