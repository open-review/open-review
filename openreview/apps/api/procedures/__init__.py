from django.conf.urls import url
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse
from openreview.apps.api.procedures.preview import PreviewProcedure
from openreview.apps.api.procedures.vote import VoteProcedure


__all__ = [
    "get_url_patterns"
    "ProcedureViewSet",
    "PreviewProcedure"
]

PROCEDURES = [PreviewProcedure, VoteProcedure]

def get_procedure_name(viewcls):
    """
    Returns lowercase name of viewclass or if it ends in Procedure the same
    name but with the last part stripped.

    >>> class Foo:
    >>>     pass
    >>>
    >>> class BarProcedure:
    >>>     pass
    >>>
    >>> get_procedure_name(Foo)
    foo
    >>> get_procedure_name(BarProcedure):
    bar
    """
    name = viewcls.__name__
    if name.endswith("Procedure"):
        name = name[:-9]
    return name.lower()

def get_url_name(viewcls):
    """Returns urlname (used in urlpatterns) for this view."""
    return "procedure-%s" % get_procedure_name(viewcls)

def get_url_pattern(viewcls):
    """Returns url with regex '{name}' and urlname 'procedure-{name}'"""
    name = get_procedure_name(viewcls)
    return url(
        view=viewcls.as_view(),
        regex=r"^{name}$".format(**locals()),
        name="procedure-{name}".format(**locals()))

urlpatterns = list(map(get_url_pattern, PROCEDURES))

class ProcedureViewSet(viewsets.ViewSet):
    """
    A procedure is a API-call which does not directly correspond or does not
    have a 1:1 create / list / retrieve mapping to a Django Model. Each procedure
    takes it own arguments, so please read their documentation carefully.
    """
    def list(self, request):
        return Response({
            get_procedure_name(viewcls): reverse(get_url_name(viewcls), request=request)
            for viewcls in PROCEDURES
        })
