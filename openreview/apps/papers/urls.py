from django.conf.urls import patterns, url
from openreview.apps.papers.views import PaperWithReviewsView

urlpatterns = patterns('',
    url(r'^(?P<id>\d+)/$', PaperWithReviewsView.as_view(), name="paper")
)
