from rest_framework import viewsets, serializers
from openreview.apps.api.fields import RelativeField
from openreview.apps.api.viewsets.paper import PaperSerializer
from openreview.apps.main.models import Keyword, Paper
from openreview.apps.tools.views import ModelSerializerMixin


class PaperViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    model = Paper
    model_serializer_class = PaperSerializer

    def get_queryset(self):
        return self.objects.keyword.papers.all()

class KeywordSerializer(serializers.HyperlinkedModelSerializer):
    papers = RelativeField()

    class Meta:
        model = Keyword

class KeywordViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    model = Keyword
    model_serializer_class = KeywordSerializer