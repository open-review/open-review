from rest_framework import viewsets
from openreview.apps.api.serializers import CustomHyperlinkedModelSerializer
from openreview.apps.main.models import Category, Paper
from openreview.apps.tools.views import ModelSerializerMixin


class CategorySerializer(CustomHyperlinkedModelSerializer):
    class Meta:
        model = Category

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Categories are fixed and can only change between releases of OpenReview. Each
    category contains a property `arxiv_code` which is used on
    [arXiv.org](http://arxiv.org/).
    """
    model = Category
    model_serializer_class = CategorySerializer

class PaperViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    model = Paper

    def get_serializer_class(self):
        # Prevent circular import
        from openreview.apps.api.viewsets.paper import PaperSerializer
        return PaperSerializer

    def get_queryset(self):
        return self.objects.category.papers
