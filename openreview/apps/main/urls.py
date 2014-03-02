from django.conf.urls import patterns, url

from openreview.apps.main.views import frontpage


urlpatterns = patterns('',
    url('^$', frontpage, name="frontpage")
)
