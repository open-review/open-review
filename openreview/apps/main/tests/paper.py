from django.test import TestCase
from openreview.apps.tools.testing import create_test_paper

__all__ = ["TestPaper"]

class TestPaper(TestCase):
    def test_get_reviews_comments(self):
        print("HALLO")
        paper = create_test_paper(n_authors=0, n_keywords=1, n_comments=2, n_reviews=3)
        self.assertEqual(paper.get_reviews().count(), 3)
        self.assertEqual(paper.get_comments().count(), 2)
        self.assertNotEqual(paper.reviews.all().count(), 3)

    def get_votes(self):
        pass

