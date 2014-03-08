from django.conf.urls import patterns, url

from openreview.apps.main.views import frontpage
from openreview.apps.main.views import add_review


urlpatterns = patterns('',
    url('^$', frontpage, name="frontpage"),
    url('^review/add$', add_review, name="add_review")
)
