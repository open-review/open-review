from django.conf.urls import patterns, url

from openreview.apps.main.views import landing_page
from openreview.apps.main.views import dashboard
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    url('^$', landing_page, name="landing_page"),
    url('^dashboard$', dashboard, name="dashboard"),
    url(r'^about/team', TemplateView.as_view(template_name='main/team.html'), name='team'),
    url(r'^about/mission$', TemplateView.as_view(template_name='main/mission.html'), name="mission")
)
