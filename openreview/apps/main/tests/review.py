import unittest
from openreview.apps.main.models import Review, set_n_votes_cache
from openreview.apps.tools.testing import create_test_review, create_test_votes, assert_max_queries, list_queries

__all__ = ["TestReview"]

class TestReview(unittest.TestCase):
    def setUp(self):
        self.review = create_test_review()

        create_test_votes(review=self.review, counts={
            -3: 2,
            -1: 2,
            1: 3,
            2: 1
        })

    def test_n_downvotes(self):
        self.assertEqual(0, create_test_review().n_downvotes)
        self.assertEqual(8, self.review.n_downvotes)

    def test_n_upvotes(self):
        self.assertEqual(0, create_test_review().n_upvotes)
        self.assertEqual(5, self.review.n_upvotes)

    def test_set_n_votes_cache(self):
        review1 = self.review
        self.setUp()
        review2 = self.review

        # 5 queries must be done without caching
        with list_queries(destination=[]) as l:
            self.assertEqual(review1.n_downvotes, 8)
            self.assertEqual(review2.n_downvotes, 8)
            self.assertEqual(review1.n_upvotes, 5)
            self.assertEqual(review2.n_upvotes, 5)
        self.assertEqual(len(l), 4)

        reviews = set(Review.objects.filter(id__in=(review1.id, review2.id)))
        with assert_max_queries(n=2):
            set_n_votes_cache(reviews)

        review1, review2 = reviews
        with assert_max_queries(n=0):
            self.assertEqual(review1.n_downvotes, 8)
            self.assertEqual(review2.n_downvotes, 8)
            self.assertEqual(review1.n_upvotes, 5)
            self.assertEqual(review2.n_upvotes, 5)


