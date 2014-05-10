from openreview.apps.tools.testing import BaseTestCase

from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from openreview.apps.main.models import Vote
from openreview.apps.tools.testing import create_test_review, create_test_user, create_test_vote

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

    def test_can_delete(self):
        vote = create_test_vote()
        self.assertFalse(vote.can_delete(AnonymousUser()))
        self.assertFalse(vote.can_delete(create_test_user()))
        self.assertTrue(vote.can_delete(vote.voter))

    def test_can_change(self):
        # Same as can_delete for now
        pass

