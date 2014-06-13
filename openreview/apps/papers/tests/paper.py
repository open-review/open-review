from django.core.urlresolvers import reverse
from django.test import Client
from selenium.common.exceptions import NoSuchElementException

from openreview.apps.tools.testing import BaseTestCase
from openreview.apps.tools.testing import create_test_paper, assert_max_queries, create_test_user, SeleniumTestCase


__all__ = ["TestPaperViewLive"]

class TestPaperViewLive(SeleniumTestCase):
    def setUp(self):
        self.paper = create_test_paper(2, 2, 2, 2)
        self.client = Client()

    def test_new_review(self):
        """
        Merely clicking on 'new review' textarea should span a preview
        """
        self.login()

        self.open(reverse("paper", args=[create_test_paper().id]))
        self.assertRaises(NoSuchElementException, self.wd.find_css, ".preview .review")
        self.wd.find_css(".compose-top-level textarea").click()
        self.wd.wait_for_css(".preview .review")
