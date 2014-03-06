from django.conf.urls import patterns, include, url
from openreview.apps.papers.views import PaperWithReviewsView

urlpatterns = patterns('',
    url(r'^(?P<id>\d+)/$', PaperWithReviewsView.as_view())
)
