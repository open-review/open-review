from django.conf.urls import patterns, include, url

from rest_framework import routers
from openreview.apps.api import procedures
from openreview.apps.api.procedures import ProcedureViewSet

from openreview.apps.api.viewsets import user, paper, author, category, keyword
from openreview.apps.api.viewsets.keyword import KeywordViewSet

top_router = routers.DefaultRouter()
top_router.register(r'users', user.UserViewSet)
top_router.register(r'papers', paper.PaperViewSet)
top_router.register(r'authors', author.AuthorViewSet)
top_router.register(r'categories', category.CategoryViewSet)
top_router.register(r'keywords', KeywordViewSet)
top_router.register(r'procedures', ProcedureViewSet, base_name="procedure")

users_router = routers.DefaultRouter()
users_router.register(r'reviews', user.ReviewViewSet)
users_router.register(r'votes', user.VoteViewSet)

papers_router = routers.DefaultRouter()
papers_router.register(r'reviews', paper.ReviewViewSet)
papers_router.register(r'authors', paper.AuthorViewSet)
papers_router.register(r'keywords', paper.KeywordViewSet)

keywords_router = routers.DefaultRouter()
keywords_router.register(r'papers', keyword.PaperViewSet)

categories_router = routers.DefaultRouter()
categories_router.register(r'papers', category.PaperViewSet)

procedures_router = routers.DefaultRouter()

urlpatterns = patterns('',
    url(r'^', include(top_router.urls)),
    url(r'^users/(?P<user_id>[0-9]+)/', include(users_router.urls)),
    url(r'^papers/(?P<paper_id>[0-9]+)/', include(papers_router.urls)),
    url(r'^keywords/(?P<keyword_id>[0-9]+)/', include(keywords_router.urls)),
    url(r'^categories/(?P<category_id>[0-9]+)/', include(categories_router.urls)),
    url(r'^procedures/', include(procedures.urlpatterns)),
)

# Set API root documentation
api_root = top_router.urls[0].callback.cls
api_root.__doc__ = """
Filtering is not yet enabled. You can use nested properties to fetch all papers for a
given keyword, etc.
"""


