from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^events/$', views.CalendarEventsView.as_view(), name='user-events'),
    url(r'^events/(?P<uuid>[0-9a-f]{32})/$',
        views.CalendarEventView.as_view(), name='event'),
    url(r'^events/attendees/(?P<uuid>[0-9a-f]{32})/$',
        views.AttendanceView.as_view(), name='attendance'),
]
