from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

urlpatterns = patterns('',
    url(r'^accounts/', include("openreview.apps.accounts.urls")),
    url(r'^papers/', include("openreview.apps.papers.urls")),
    url(r'^', include("openreview.apps.main.urls")),

    # Django rest framework has internal views which can authenticate users
    # in its browseable interface
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/', include('openreview.apps.api.urls')),
    url(r'^api/$', RedirectView.as_view(url='./v1', permanent=False)),
)
