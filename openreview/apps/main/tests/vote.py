from django.db import IntegrityError
from openreview.apps.main.models import Vote
from openreview.apps.tools.testing import create_test_review, create_test_user, BaseTestCase

__all__ = ["TestVote"]


class TestVote(BaseTestCase):
    def test_save(self):
        user = create_test_user()
        review = create_test_review()

        vote = Vote(review=review, voter=user)
        vote.save()

        # You cannot vote twice on one review
        vote = Vote(review=review, voter=user)
        self.assertRaises(IntegrityError, vote.save)
