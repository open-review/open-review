from django.conf.urls import patterns, include, url
from django.contrib import admin
from haystack import admin as admin2

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include("openreview.apps.accounts.urls")),
    url(r'^papers/', include("openreview.apps.papers.urls")),
    url(r'^', include("openreview.apps.main.urls"))
)

