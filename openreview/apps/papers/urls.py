from django.conf.urls import patterns, url

from openreview.apps.papers.views import SearchView
from openreview.apps.papers.views import PaperWithReviewsView, PapersView, VoteView, ReviewView, PreviewView, \
    AddPaperView
from openreview.apps.papers.views import doi_scraper, arxiv_scraper


urlpatterns = patterns('',
    url(r'^new$', PapersView.as_view(order='new'), name='new'),
    url(r'^trending$', PapersView.as_view(order='trending'), name='trending'),
    url(r'^controversial$', PapersView.as_view(order='controversial'), name='controversial'),
    url(r'^search/$', SearchView.as_view(), name="search-paper"),
    url(r'^add$', AddPaperView.as_view(), name='add'),
    url(r'^(?P<paper_id>\d+)/$', PaperWithReviewsView.as_view(), name="paper"),
    url(r'^(?P<paper_id>\d+)/review/(?P<review_id>\d+)/vote$', VoteView.as_view(), name="vote"),
    url(r'^(?P<paper_id>\d+)/review/(?P<review_id>\-?\d+)$', ReviewView.as_view(), name="review"),
    url(r'^(?P<paper_id>\d+)/preview$', PreviewView.as_view(), name="preview"),
    url(r'^doi/(?P<id>[a-zA-Z0-9.]*)', doi_scraper, name="doi-scraper"),
    url(r'^arxiv/(?P<doc_id>[a-zA-Z0-9.]*)', arxiv_scraper, name="arxiv-scraper")
)
