from django.conf.urls import patterns, url

from openreview.apps.main.views import landing_page
from openreview.apps.main.views import dashboard
from openreview.apps.main.views import add_review

urlpatterns = patterns('',
    url('^$', landing_page, name="landing_page"),
    url('^dashboard$', dashboard, name="dashboard"),
    url('^review/add$', add_review, name="add_review")
)
