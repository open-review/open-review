from rest_framework import viewsets

from openreview.apps.api.fields import RelativeField, CustomHyperlinkedRelatedField
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

    authors = CustomHyperlinkedRelatedField(many=True, view_name="author-detail")
    keywords = CustomHyperlinkedRelatedField(many=True, view_name="keyword-detail")
    categories = CustomHyperlinkedRelatedField(many=True, view_name="category-detail")

    class Meta:
        model = Paper

class PaperViewSet(ModelSerializerMixin, viewsets.ModelViewSet):
    """
    Although not explicitly said below, you can use `./authors` and `./keywords` to
    fetch more details about both related fields.

    POST accepts JSON for the fields `authors`, `keywords` and `categories`. You can
    either specify integers or API urls (existing objects, their primary keys) or an object
    representing a serialised `author`, `keyword` or `category`. For example, you might
    use the following request to create a paper:


        {
          "doc_id": "doi:10.1002/0470841559.ch1",
          "title": "Bitcoin: A Peer-to-Peer Electronic Cash System",
          "abstract": "...",
          "urls": null,
          "publish_date": "2014-03-06",
          "publisher": null,

          "authors": [1],
          "keywords": [2, 12],
          "categories": [4, 9],

          "categories": [
            "http://localhost:8000/api/v1/categories/2/",
            "http://localhost:8000/api/v1/categories/10/"
          ],
        }

    You may use primary keys *and* urls as identifiers.
    """
    model = Paper
    model_serializer_class = PaperSerializer
