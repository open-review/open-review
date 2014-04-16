from rest_framework import viewsets, serializers

from openreview.apps.api.fields import HyperlinkedRelatedFieldOrNone
from openreview.apps.main.models import Review


def show_poster(user, review):
    # Show poster of review if currently logged in user is poster, or if review
    # is not anonymous
    return review.poster == user or not review.anonymous

class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    poster = HyperlinkedRelatedFieldOrNone(show_poster, view_name="user-detail")

    class Meta:
        model = Review


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    model = Review
    serializer_class = ReviewSerializer
