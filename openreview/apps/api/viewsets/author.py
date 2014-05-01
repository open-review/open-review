from rest_framework import viewsets, serializers
from openreview.apps.api.serializers import CustomHyperlinkedModelSerializer
from openreview.apps.main.models import Author


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    model = Author

class AuthorSerializer(CustomHyperlinkedModelSerializer):
    class Meta:
        model = Author
