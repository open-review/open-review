from django.conf.urls import patterns, url
from main.views import frontpage

urlpatterns = patterns('',
    url('^$', frontpage, name="frontpage")
)
