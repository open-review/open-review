from django.conf.urls import patterns, url
from openreview.apps.papers.views import PaperWithReviewsView, VoteView

urlpatterns = patterns('',
    url(r'^(?P<paper_id>\d+)/$', PaperWithReviewsView.as_view(), name="paper"),
    url(r'^(?P<paper_id>\d+)/review/(?P<review_id>\d+)/vote$', VoteView.as_view(), name="vote")
)
