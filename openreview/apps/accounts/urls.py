from django.conf.urls import patterns, url

from openreview.apps.accounts.views import LoginView, LogoutView


urlpatterns = patterns('',
    url('^login/$', LoginView.as_view(), name="accounts-login"),
    url('^register/$', LoginView.as_view(), name="accounts-register"),
    url('^logout/$', LogoutView.as_view(), name="accounts-logout")
)
