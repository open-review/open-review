from django.test import TestCase
from django.core.urlresolvers import reverse
import unittest
from datetime import date
from openreview.apps.tools.testing import SeleniumTestCase
from openreview.apps.tools.testing import create_test_author, create_test_paper, create_test_user

from openreview.apps.main.models import Paper,Review

__all__ = ["TestReviewForm"]

class TestReviewForm(SeleniumTestCase):
    def setUp(self):
        self.a = create_test_author(name="tester")
        self.u = create_test_user()
        super().setUp()


    def test_paper_gets_committed(self):
        self.open(reverse("add_review"))
        # Check if redirected to login if not logged in
        self.assertTrue(self.wd.current_url.endswith("{login}?next={next}".format(login=reverse("accounts-login"), next=reverse("add_review"))))
        self.wd.wait_for_css("body")
        self.wd.find_css("#id_login_username").send_keys(self.u.username)
        self.wd.find_css("#id_login_password").send_keys("test")
        self.wd.find_css('input[value="Login"]').click()
        # Check if on the right page now
        self.assertFalse(reverse("accounts-login") in self.wd.current_url)
        self.assertTrue(self.wd.current_url.endswith(reverse("add_review")))
        self.wd.wait_for_css("#id_title")

        # Select the right paper
        self.wd.find_css("#id_title").send_keys("Some fancy paper title")
        self.wd.find_css("#id_doc_id").send_keys("1403.0438")
        self.wd.find_css("#id_authors").send_keys("Jéan-Pièrre van 't Hoff")
        self.wd.find_css("#id_abstract").send_keys("This paper is fancy.")
        self.wd.find_css("#id_publish_date").send_keys("2012-01-01")
        self.wd.find_css("#id_publisher").send_keys("Springer")
        self.wd.find_css("#id_urls").send_keys("http://example.org/document.pdf")
        self.wd.find_css("#id_text").send_keys("test\nlol\ndoei")
        self.wd.find_css("input[name=\"add_review\"]").click()
        self.wd.wait_for_css("body")

        # Review is saved well
        p = Paper.objects.get(title="Some fancy paper title")        
        self.assertEqual(p.doc_id,"1403.0438")
        #self.assertEqual(p.publish_date, "Jéan-Pièrre van 't Hoff")
        self.assertEqual(p.abstract, "This paper is fancy.")
        self.assertEqual(p.publish_date, date(2012,1,1))        
        self.assertEqual(p.publisher, "Springer")        
        self.assertEqual(p.urls, "http://example.org/document.pdf")

        self.assertTrue(Review.objects.count() == 1);
        r = Review.objects.get(paper=p.id)                    
        self.assertEqual(r.poster, self.u)
        self.assertEqual(r.text.replace("\r", ""), "test\nlol\ndoei")