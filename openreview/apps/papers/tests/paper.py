import unittest

from django.core.urlresolvers import reverse
from django.test import Client

from openreview.apps.tools.testing import create_test_paper, assert_max_queries, create_test_user

__all__ = ["TestPaperWithReviewsView"]

class TestPaperWithReviewsView(unittest.TestCase):
    def setUp(self):
        self.paper = create_test_paper(2, 2, 2, 2)
        self.client = Client()

    def test_queries_anonymous(self):
        with assert_max_queries(n=7):
            self.client.get(reverse("paper", args=[self.paper.id]))

    def test_queries_logged_in(self):
        create_test_user(username="abc", password="123")
        self.assertTrue(self.client.login(username="abc", password="123"))

        with assert_max_queries(n=9):
            self.client.get(reverse("paper", args=[self.paper.id]))