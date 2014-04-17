from rest_framework import viewsets
from rest_framework.relations import RelatedField

from openreview.apps.api.fields import RelativeField
from openreview.apps.api.serializers import CustomHyperlinkedModelSerializer
from openreview.apps.api.viewsets.review import ReviewSerializer
from openreview.apps.main.models import Paper, Review, Author, Keyword
from openreview.apps.tools.views import ModelSerializerMixin


class ReviewViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    model = Review
    model_serializer_class = ReviewSerializer

    def get_queryset(self):
        return self.objects.paper.reviews.all()

class AuthorViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    model = Author

class KeywordViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    model = Keyword

class PaperSerializer(CustomHyperlinkedModelSerializer):
    reviews = RelativeField()
    authors = RelatedField(many=True)
    keywords = RelatedField(many=True)
    categories = RelatedField(many=True)

    class Meta:
        model = Paper

class PaperViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    Although not explicitly said below, you can use `./authors` and `./keywords` to
    fetch more details about both related fields.
    """
    model = Paper
    model_serializer_class = PaperSerializer
