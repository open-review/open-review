from django.core.urlresolvers import reverse
from django.test import Client
from openreview.apps.tools.testing import BaseTestCase as TestCase
from openreview.apps.tools.testing import create_test_paper

__all__ = ["TestSearchView"]

class TestSearchView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("search-paper")
        super().setUp()

    def test_empty_query(self):
        c = self.client.get(self.url)
        self.assertTrue(b"no results" in c.content.lower())

        c = self.client.get(self.url + "?q=")
        self.assertTrue(b"no results" in c.content.lower())

    def test_non_empty(self):
        create_test_paper(title="Bitcoin in headline!")

        # This result must be in elastic
        c = self.client.get(self.url + "?q=bitcoin")
        self.assertTrue(b"Bitcoin in headline!" in c.content)

        # This result probably isn't in elastic :)
        c = self.client.get(self.url + "?q=jameson")
        self.assertTrue(b"no results" in c.content.lower())
