from django.conf.urls import patterns, url

from openreview.apps.main.views import frontpage
from openreview.apps.main.views import addreview


urlpatterns = patterns('',
    url('^$', frontpage, name="frontpage"),
    url('^review/add$', addreview, name="addreview")
)
