
import unittest
from django.core.urlresolvers import reverse
from django.test import Client
from selenium.common.exceptions import NoSuchElementException
import time
from openreview.apps.main.models import Review, Vote
from openreview.apps.tools.testing import assert_max_queries, create_test_paper, create_test_user, create_test_review, \
    SeleniumTestCase

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


class TestVoteView(unittest.TestCase):
    def test_get(self):
        review = create_test_review()
        paper = review.paper
        user = create_test_user(username="foo", password="bar")

        url = reverse("vote", args=[paper.id, review.id + 100000])
        self.assertFalse(Review.objects.filter(id=review.id + 100000).exists())

        c = Client()
        self.assertEqual(c.get(url).status_code, 403)
        self.assertTrue(c.login(username="foo", password="bar"))
        self.assertEqual(c.get(url).status_code, 404)

        url = reverse("vote", args=[paper.id, review.id])
        self.assertEqual(c.get(url).status_code, 400)
        self.assertEqual(c.get(url + "?vote=-2").status_code, 400)
        self.assertEqual(c.get(url + "?vote=3").status_code, 400)
        self.assertEqual(c.get(url + "?vote=0").status_code, 201)

        self.assertFalse(Vote.objects.filter(voter=user, review=review))
        self.assertEqual(c.get(url + "?vote=1").status_code, 201)
        self.assertEqual(Vote.objects.get(voter=user, review=review).vote, 1)

        self.assertEqual(c.get(url + "?vote=0").status_code, 201)
        self.assertFalse(Vote.objects.filter(voter=user, review=review))

        self.assertFalse(Vote.objects.filter(voter=user, review=review))
        self.assertEqual(c.get(url + "?vote=-1").status_code, 201)
        self.assertEqual(Vote.objects.get(voter=user, review=review).vote, -1)

class TestVoteViewLive(SeleniumTestCase):
    def test_aesthetics(self):
        # Not logged in
        paper = create_test_paper(n_reviews=2)
        review = paper.reviews.all()[0]

        self.open(reverse("paper", args=[paper.id]))
        self.wd.wait_for_css("body")

        self.assertRaises(NoSuchElementException, self.wd.find_css, ".review .login :visible")
        self.assertRaises(NoSuchElementException, self.wd.find_css, ".review .login:visible")
        self.assertEqual(2, len(self.wd.find_css(".review .login")))

        review_dom = self.wd.find_css(".review[review_id='%s']" % review.id)
        review_dom.find_element_by_class_name("upvote").click()
        self.assertTrue(review_dom.find_element_by_class_name("login").is_displayed())

        # Logged in
        user = create_test_user(username="foo2", password="bar")
        self.login("foo2", "bar")

        self.open(reverse("paper", args=[paper.id]))
        self.wd.wait_for_css("body")

        review_dom = self.wd.find_css(".review[review_id='%s']" % review.id)
        upvote = review_dom.find_element_by_class_name("upvote")
        downvote = review_dom.find_element_by_class_name("downvote")
        upvote_count = upvote.find_element_by_class_name("count")
        downvote_count = downvote.find_element_by_class_name("count")

        self.assertEqual(upvote_count.text, "0")
        self.assertEqual(downvote_count.text, "0")

        self.assertFalse(Vote.objects.filter(voter=user, review=review).exists())

        upvote.click()
        self.assertEqual(upvote_count.text, "1")
        self.assertEqual(downvote_count.text, "0")

        upvote.click()
        self.assertEqual(upvote_count.text, "0")
        self.assertEqual(downvote_count.text, "0")

        downvote.click()
        self.assertEqual(upvote_count.text, "0")
        self.assertEqual(downvote_count.text, "1")

        downvote.click()
        self.assertEqual(upvote_count.text, "0")
        self.assertEqual(downvote_count.text, "0")

        downvote.click()
        upvote.click()
        self.assertEqual(upvote_count.text, "1")
        self.assertEqual(downvote_count.text, "0")

        time.sleep(0.3)

        self.assertTrue(Vote.objects.filter(voter=user, review=review).exists())
