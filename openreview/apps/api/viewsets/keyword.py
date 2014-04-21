from rest_framework import viewsets

from openreview.apps.api.fields import RelativeField
from openreview.apps.api.serializers import CustomHyperlinkedModelSerializer
from openreview.apps.main.models import Keyword, Paper
from openreview.apps.tools.views import ModelSerializerMixin


class PaperViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    model = Paper

    def get_serializer_class(self):
        # Prevent circular import
        from openreview.apps.api.viewsets.paper import PaperSerializer
        return PaperSerializer

    def get_queryset(self):
        return self.objects.keyword.papers.all()

class KeywordSerializer(CustomHyperlinkedModelSerializer):
    papers = RelativeField()

    class Meta:
        model = Keyword

class KeywordViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    model = Keyword
    model_serializer_class = KeywordSerializer