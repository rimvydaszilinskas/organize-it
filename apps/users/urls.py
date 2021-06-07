from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.UserFilterView.as_view(), name='users'),
    url(r'^self/$', views.SelfUserView.as_view(), name='self'),
    url(r'^register/$', views.UserRegistrationView.as_view(), name='registration'),
    url(r'^login/$', views.UserAuthenticationView.as_view(), name='login'),
    url(r'^groups/$', views.UserGroupsView.as_view(), name='user-groups'),
    url(r'^groups/(?P<uuid>[0-9a-f]{32})/$',
        views.UserGroupView.as_view(), name='user-group'),
    url(r'^invitations/$', views.UserInvitationView.as_view(), name='invitation'),
    url(r'^password/$', views.UserPasswordChangeView.as_view(), name='password'),
]
