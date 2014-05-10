from django.conf.urls import patterns, url

from openreview.apps.main.views import landing_page
from openreview.apps.main.views import dashboard

urlpatterns = patterns('',
    url('^$', landing_page, name="landing_page"),
    url('^dashboard$', dashboard, name="dashboard")
)
