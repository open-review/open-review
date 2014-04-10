from django.core.urlresolvers import reverse
from django.test import Client

from openreview.apps.tools.testing import create_test_paper, BaseTestCase

__all__ = ["TestPapersView"]

class TestPapersView(BaseTestCase):

    def test_get(self): 
        create_test_paper()   
        c = Client()
        subpages = subpages = ["new","trending","controversial"];
        for subpage in subpages:
            url = reverse(subpage)
            self.assertEqual(c.get(url).status_code, 200)
            self.assertEqual(c.get(url + "?p=0").status_code, 200)
            self.assertEqual(c.get(url + "?p=1").status_code, 200)
            self.assertEqual(c.get(url + "?p=999").status_code, 200)
            self.assertEqual(c.get(url + "?p=-1").status_code, 404)
            self.assertEqual(c.get(url + "?p=").status_code, 404)
            self.assertEqual(c.get(url + "?p=abc").status_code, 404)
            self.assertEqual(c.get(url + "?p=1abc").status_code, 404)