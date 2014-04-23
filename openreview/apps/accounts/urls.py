from django.conf.urls import patterns, url

from openreview.apps.accounts.views import LoginView, LogoutView, SettingsView, AccountDeleteView


urlpatterns = patterns('',
    url('^login/$', LoginView.as_view(), name="accounts-login"),
    url('^register/$', LoginView.as_view(), name="accounts-register"),
    url('^logout/$', LogoutView.as_view(), name="accounts-logout"),
    url('^settings/$', SettingsView.as_view(), name="accounts-settings"),
    url('^delete/$', AccountDeleteView.as_view(), name="accounts-delete")
)
