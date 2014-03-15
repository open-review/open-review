import unittest
from django.core.urlresolvers import reverse
from django.test import Client
from selenium.common.exceptions import NoSuchElementException
from openreview.apps.main.models import Paper, Review
from openreview.apps.tools.testing import create_test_user, create_test_review, SeleniumTestCase, create_test_paper


class TestReviewView(unittest.TestCase):
    def test_get(self):
        pass

    def test_delete(self):
        user = create_test_user(username="f", password="f")
        review = create_test_review(poster=create_test_user())

        url = reverse("review", args=[review.paper.id, review.id])
        c = Client()

        self.assertEqual(c.delete(url).status_code, 403)
        c.login(username="f", password="f")
        self.assertEqual(c.delete(url).status_code, 403)
        review = create_test_review(poster=user)
        url = reverse("review", args=[review.paper.id, review.id])
        self.assertEqual(c.delete(url).status_code, 200)

    def test_post(self):
        c = Client()

        self.assertFalse(Paper.objects.filter(id=0).exists())
        self.assertFalse(Review.objects.filter(id=0).exists())

        url = reverse("review", args=[0, 0])
        user = create_test_user(username="food", password="pizza")

        # Not logged in
        response = c.post(url)
        self.assertEqual(403, response.status_code)

        # No text provided
        c.login(username="food", password="pizza")
        response = c.post(url)
        self.assertEqual(400, response.status_code)

        # Paper not found
        response = c.post(url, dict(text="foo"))
        self.assertEqual(404, response.status_code)

        # Review not found
        response = c.post(url, dict(text="foo"))
        self.assertEqual(404, response.status_code)

        # Cannot create review with paper != given paper
        paper = create_test_paper()
        review = create_test_review()
        url = reverse("review", args=[paper.id, review.id])
        self.assertNotEqual(review.paper, paper)
        response = c.post(url, dict(text="foo", submit="blaat"))
        self.assertEqual(400, response.status_code)

        # We can if we don't commit
        response = c.post(url, dict(text="foo"))
        self.assertEqual(200, response.status_code)

        # Finally a successful try
        url = reverse("review", args=[review.paper.id, review.id])
        c.post(url, dict(text="foo-post-test", submit="blaat"))
        self.assertTrue(Review.objects.filter(text="foo-post-test", parent=review, poster=user).exists())


class TestReviewViewLive(SeleniumTestCase):
    def test_aesthetics(self):
        # Are own submissions coloured differently?
        user = create_test_user(username="testdelete", password="123")

        r1 = create_test_review(poster=user)
        r2 = create_test_review(paper=r1.paper)

        self.login("testdelete", "123")
        self.open(reverse("paper", args=[r1.paper.id]))
        self.wd.wait_for_css("body")

        self.wd.find_css(".review.bs-callout-info[review_id='%s']" % r1.id)
        self.assertRaises(NoSuchElementException, self.wd.find_css, ".review.bs-callout-success[review_id='%s']" % r2.id)

    def test_latex(self):
        pass
