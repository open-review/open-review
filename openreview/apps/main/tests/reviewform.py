from django.test import TestCase
from django.core.urlresolvers import reverse
import time

from openreview.apps.tools.testing import SeleniumTestCase, disable_pipeline
from openreview.apps.tools.testing import create_test_author, create_test_paper

from openreview.apps.main.models import *

__all__ = ["TestReviewForm"]

class TestReviewForm(SeleniumTestCase):
	def setUp(self):
		self.a = create_test_author(name="tester")
		self.b = create_test_paper()
		super().setUp()


	def test_paper_gets_committed(self):
		print(reverse("addreview"))
		self.open(reverse("addreview"))
		self.wd.wait_for_css("body")
		time.sleep(5)
		self.wd.find_css("#id_paper").value(self.b.id)
		time.sleep(10)
		pass
