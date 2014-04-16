from rest_framework import viewsets
from openreview.apps.api.viewsets.paper import PaperSerializer
from openreview.apps.main.models import Category, Paper
from openreview.apps.tools.views import ModelSerializerMixin


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Categories are fixed and can only change between releases of OpenReview. Each
    category contains a property `arxiv_code` which is used on
    [arXiv.org](http://arxiv.org/).
    """
    model = Category

class PaperViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    model = Paper
    model_serializer_class = PaperSerializer

    def get_queryset(self):
        return self.objects.category.papers
