from rest_framework import viewsets

from openreview.apps.accounts.models import User
from openreview.apps.api.fields import RelativeField
from openreview.apps.api.serializers import CustomHyperlinkedModelSerializer
from openreview.apps.api.viewsets.review import ReviewSerializer
from openreview.apps.main.models import Review, Vote
from openreview.apps.tools.views import ModelSerializerMixin


NON_OWNER_FIELDS = (
    "id", "username", "password", "date_joined", "is_active", "url",
    "reviews", "votes"
)

class ReviewViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    Anonymous reviews are not displayed (unless you're logged in and viewing your
    own users' contributions).
    """
    model = Review
    model_serializer_class = ReviewSerializer

    def get_queryset(self):
        reviews = self.objects.user.reviews
        if self.request.user != self.objects.user:
            return reviews.filter(anonymous=False)
        return reviews.all()

class VoteViewSet(ModelSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    If user has set `votes_public` to `False` (default) no votes are displayed. You
    cannot vote twice on the same post: if a duplicate vote is detected, the first one
    will be overridden.
    """
    model = Vote

    def get_queryset(self):
        if not self.objects.user.votes_public:
            return Vote.objects.none()
        return self.objects.user.votes.all()

class UserSerializer(CustomHyperlinkedModelSerializer):
    reviews = RelativeField()
    votes = RelativeField()

    def get_fields(self):
        fields = super().get_fields()

        many = self.many or (self.object is None and self.many is None)
        if many or self.object.id is not self.request.user.id:
            fields = dict((field_name, fields[field_name]) for field_name in NON_OWNER_FIELDS)

        # Always exclude password field
        del fields["password"]
        return fields

    class Meta:
        model = User

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Displays fields `id`, `is_active`, `date_joined`, `username` which are mapped 1:1 to
    the model User. If the detailed view of the logged in user is request, additional
    fields are displayed. The field `password` is always hidden.
    """
    model = User
    serializer_class = UserSerializer
