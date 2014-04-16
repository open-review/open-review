from rest_framework import viewsets, serializers
from openreview.apps.main.models import Author


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    model = Author
