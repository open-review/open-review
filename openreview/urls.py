import functools

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve

admin.autodiscover()

from django.conf import settings

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include("openreview.apps.accounts.urls")),
    url(r'^papers/', include("openreview.apps.papers.urls")),
    url(r'^', include("openreview.apps.main.urls"))
)

if settings.FORCE_STATICFILES and not settings.DEBUG:
    # Django staticfiles is very wary of running with DEBUG=True. We need this for testing with
    # Travis however, which is why we override all warnings.
    print("Warning: FORCE_STATICFILES is an insecure option and should never be used in production")

    settings.DEBUG = True
    try:
        view = functools.partial(serve, insecure=True)
        urlpatterns += static(settings.STATIC_URL, view=view)
    finally:
        settings.DEBUG = False

