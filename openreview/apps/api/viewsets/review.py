from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.fields import Field

from openreview.apps.api.fields import HyperlinkedRelatedFieldOrNone
from openreview.apps.api.serializers import CustomHyperlinkedModelSerializer
from openreview.apps.main.forms import VISIBILITY_CHOICES
from openreview.apps.main.models import Review, set_n_votes_cache


def show_poster(user, review):
    # Show poster of review if currently logged in user is poster, or if review
    # is not anonymous
    if review is None:
        return False
    return review.poster == user or not review.anonymous

class ReviewSerializer(CustomHyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    poster = HyperlinkedRelatedFieldOrNone(show_poster, view_name="user-detail")
    n_upvotes = Field(source="n_upvotes")
    n_downvotes = Field(source="n_downvotes")

    def restore_object(self, attrs, instance=None):
        # We want to prevent users creating loops, so we disable parents changing.
        if instance is not None and "parent" in attrs:
            raise PermissionDenied("You cannot change a reviews parent.")

        review = super().restore_object(attrs=attrs, instance=instance)

        # Set visibility manually, as it is not a model field
        # TODO: Incorporate form logic somehow?
        visibility = self.request.DATA.get("visibility")
        if visibility is not None:
            if visibility not in VISIBILITY_CHOICES:
                raise APIException(dict(visibility=["%s not one of the available choices." % visibility]))
            getattr(review, "set_%s" % visibility)()

        return review


    class Meta:
        model = Review

class ReviewViewSet(viewsets.ModelViewSet):
    model = Review
    serializer_class = ReviewSerializer

    def paginate_queryset(self, queryset, page_size=None):
        page = super().paginate_queryset(queryset, page_size)
        set_n_votes_cache(page.object_list)
        return page
