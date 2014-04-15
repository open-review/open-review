import unittest

from django.core.urlresolvers import reverse
from django.test import Client
from selenium.common.exceptions import NoSuchElementException

from openreview.apps.tools.testing import create_test_paper, assert_max_queries, create_test_user, SeleniumTestCase

__all__ = ["TestPaperWithReviewsView", "TestPaperViewLive"]

class TestPaperWithReviewsView(unittest.TestCase):
    def setUp(self):
        self.paper = create_test_paper(2, 2, 2, 2)
        self.client = Client()

    def test_queries_anonymous(self):
        with assert_max_queries(n=8):
            self.client.get(reverse("paper", args=[self.paper.id]))

    def test_queries_logged_in(self):
        create_test_user(username="abc", password="123")
        self.assertTrue(self.client.login(username="abc", password="123"))

        with assert_max_queries(n=9):
            self.client.get(reverse("paper", args=[self.paper.id]))

class TestPaperViewLive(SeleniumTestCase):
    def test_new_review(self):
        """
        Merely clicking on 'new review' textarea should span a preview
        """
        self.login()

        self.open(reverse("paper", args=[create_test_paper().id]))
        self.wd.wait_for_css("body")
        self.assertRaises(NoSuchElementException, self.wd.find_css, ".preview .review")
        self.wd.find_css(".new-review textarea").click()
        self.wd.wait_for_css(".preview .review")
