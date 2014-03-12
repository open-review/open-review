from django.conf.urls import patterns, url
from openreview.apps.papers.views import PaperWithReviewsView, doi_scraper, arxiv_scraper

urlpatterns = patterns('',

    url(r'^(?P<paper_id>\d+)/$', PaperWithReviewsView.as_view(), name="paper"),
    url(r'^doi/(?P<id>[a-zA-Z0-9.]*)',doi_scraper, name="doi-scraper"),
    url(r'^arxiv/(?P<id>[a-zA-Z0-9.]*)',arxiv_scraper, name="arxiv-scraper")

)
