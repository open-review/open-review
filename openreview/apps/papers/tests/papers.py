from django.core.urlresolvers import reverse
from django.test import Client

from openreview.apps.tools.testing import create_test_paper, BaseTestCase

__all__ = ["TestPapersView"]


class TestPapersView(BaseTestCase):
    def test_get(self):
        create_test_paper()
        c = Client()

        subpages = ["new", "trending", "controversial"]
        for subpage in subpages:
            url = reverse(subpage)
            self.assertEqual(c.get(url).status_code, 200)
            self.assertEqual(c.get(url + "?page=0").status_code, 200)
            self.assertEqual(c.get(url + "?page=1").status_code, 200)
            self.assertEqual(c.get(url + "?page=999").status_code, 200)
            self.assertEqual(c.get(url + "?page=-1").status_code, 404)
            self.assertEqual(c.get(url + "?page=").status_code, 404)
            self.assertEqual(c.get(url + "?page=abc").status_code, 404)
            self.assertEqual(c.get(url + "?page=1abc").status_code, 404)
