from openreview.apps.main.models import Paper
from openreview.apps.tools.testing import create_test_paper, BaseTestCase

__all__ = ["TestPaper"]


class TestPaper(BaseTestCase):
    def test_get_reviews_comments(self):
        paper = create_test_paper(n_authors=0, n_keywords=1, n_comments=2, n_reviews=3)
        self.assertEqual(paper.get_reviews().count(), 3)
        self.assertEqual(paper.get_comments().count(), 2)
        self.assertNotEqual(paper.reviews.all().count(), 3)
        self.assertEqual(paper.num_reviews(), paper.get_reviews().count())

    def test_home_columns(self):
        Paper.objects.all().delete()

        self.assertEqual(len(Paper.objects.all()), 0);
        non_trending = create_test_paper(n_authors=0, n_keywords=0, n_comments=0, n_reviews=1)
        trending = create_test_paper(n_authors=0, n_keywords=1, n_comments=2, n_reviews=3)
        empty = create_test_paper(n_authors=0, n_keywords=1, n_comments=0, n_reviews=0)
        self.assertEqual(len(Paper.objects.all()), 3)

        self.assertEqual(Paper.trending()[0], trending)
        self.assertEqual(Paper.trending()[1], non_trending)
        self.assertEqual(len(Paper.trending()), 2)

        self.assertIn(trending, Paper.latest())
        self.assertIn(non_trending, Paper.latest())
        self.assertIn(trending, Paper.controversial())
        self.assertIn(non_trending, Paper.controversial())
        self.assertEqual(len(Paper.latest()), 3)

        # TODO: test controversiality
        #self.assertEqual(len(Paper.controversial()), 2)

    def get_votes(self):
        pass
