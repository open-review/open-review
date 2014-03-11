import unittest
from openreview.apps.tools.testing import create_test_review, create_test_votes

__all__ = ["TestReview"]

class TestReview(unittest.TestCase):
    def test_n_downvotes(self):
        review = create_test_review()
        self.assertEqual(0, review.n_downvotes)

        create_test_votes(review=review, counts={
            -3: 2,
            -1: 2,
            1: 3,
            2: 1
        })

        self.assertEqual(8, review.n_downvotes)

    def test_n_upvotes(self):
        review = create_test_review()
        self.assertEqual(0, review.n_upvotes)

        create_test_votes(review=review, counts={
            -3: 2,
            -1: 2,
            1: 3,
            2: 1
        })

        self.assertEqual(5, review.n_upvotes)
