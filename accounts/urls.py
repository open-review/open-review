from django.conf.urls import patterns, url
from accounts.views import login

urlpatterns = patterns('',
    url('^login/$', login, name="accounts-login")
)
