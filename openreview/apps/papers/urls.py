from django.conf.urls import patterns, url

from openreview.apps.papers.views import PaperWithReviewsView, doi_scraper, arxiv_scraper, VoteView, ReviewView


urlpatterns = patterns('',
                       url(r'^(?P<paper_id>\d+)/$', PaperWithReviewsView.as_view(), name="paper"),
                       url(r'^(?P<paper_id>\d+)/review/(?P<review_id>\d+)/vote$', VoteView.as_view(), name="vote"),
                       url(r'^(?P<paper_id>\d+)/review/(?P<review_id>\-?\d+)$', ReviewView.as_view(), name="review"),

                       url(r'^doi/(?P<id>[a-zA-Z0-9.]*)', doi_scraper, name="doi-scraper"),
                       url(r'^arxiv/(?P<id>[a-zA-Z0-9.]*)', arxiv_scraper, name="arxiv-scraper")
)
