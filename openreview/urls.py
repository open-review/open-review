from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'openreview.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include("openreview.apps.accounts.urls")),
    # url(r'^papers/', include("openreview.apps.papers.urls")),
    url(r'^', include("openreview.apps.main.urls"))
)
