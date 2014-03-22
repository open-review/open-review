from django.conf.urls import patterns, url
from openreview.apps.papers.views import PaperWithReviewsView, VoteView, ReviewView, PapersView

urlpatterns = patterns('',
    url(r'^new$', PapersView.as_view(name='new')),
    url(r'^trending$', PapersView.as_view(name='trending')),
    url(r'^controversial$', PapersView.as_view(name='controversial')),        
    url(r'^(?P<paper_id>\d+)/$', PaperWithReviewsView.as_view(), name="paper"),
    url(r'^(?P<paper_id>\d+)/review/(?P<review_id>\d+)/vote$', VoteView.as_view(), name="vote"),
    url(r'^(?P<paper_id>\d+)/review/(?P<review_id>\-?\d+)$', ReviewView.as_view(), name="review"),
)
