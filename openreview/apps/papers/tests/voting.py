from django.core.urlresolvers import reverse
from django.db.models import Q
from django.test import Client
from selenium.common.exceptions import NoSuchElementException

from openreview.apps.main.models import Review, Vote
from openreview.apps.tools.testing import create_test_review, SeleniumTestCase, create_test_paper, create_test_user, \
    BaseTestCase

__all__ = ["TestVoteView", "TestVoteViewLive"]


class TestVoteView(BaseTestCase):
    def test_get(self):
        review = create_test_review()
        paper = review.paper
        user = create_test_user(username="foo", password="bar")

        url = reverse("vote", args=[paper.id, review.id + 100000])
        self.assertFalse(Review.objects.filter(id=review.id + 100000).exists())

        c = Client()
        self.assertEqual(c.get(url).status_code, 302, msg="User must be logged in to vote")
        self.assertTrue(c.login(username="foo", password="bar"), msg="Login failed")
        self.assertEqual(c.get(url).status_code, 404, msg="Review should not exist")

        url = reverse("vote", args=[paper.id, review.id])
        self.assertEqual(c.post(url).status_code, 400, msg="")
        self.assertEqual(c.post(url, data=dict(vote=2)).status_code, 400)
        self.assertEqual(c.post(url, data=dict(vote=3)).status_code, 400)
        self.assertEqual(c.post(url, data=dict(vote=0)).status_code, 302)

        self.assertFalse(Vote.objects.filter(voter=user, review=review).filter(~Q(vote=0)))
        self.assertEqual(c.post(url, dict(vote=1)).status_code, 302)
        self.assertEqual(Vote.objects.get(voter=user, review=review).vote, 1)

        self.assertEqual(c.post(url, dict(vote=0)).status_code, 302)
        self.assertFalse(Vote.objects.filter(voter=user, review=review).filter(~Q(vote=0)))

        self.assertEqual(c.post(url, dict(vote=-1)).status_code, 302)
        self.assertEqual(Vote.objects.get(voter=user, review=review).vote, -1)


class TestVoteViewLive(SeleniumTestCase):
    def test_aesthetics(self):
        # Not logged in
        paper = create_test_paper(n_reviews=2)
        review = paper.reviews.all()[0]

        self.open(reverse("paper", args=[paper.id]))
        self.wd.wait_for_css("body")

        self.assertRaises(NoSuchElementException, self.wd.find_css, ".review .login-message :visible")
        self.assertRaises(NoSuchElementException, self.wd.find_css, ".review .login-message:visible")
        self.assertEqual(2, len(self.wd.find_css(".review .login-message")))

        review_dom = self.wd.find_css(".review[review_id='%s']" % review.id)
        review_dom.find_element_by_class_name("upvote").click()
        self.assertTrue(review_dom.find_element_by_class_name("login-message").is_displayed())

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

        # At least one vote should have gone through :-)
        self.assertTrue(Vote.objects.filter(voter=user, review=review).exists())

        # Can we vote on deleted submissions?
        r1, r2 = paper.reviews.all()
        r1.delete()
        r2.delete()

        self.wd.refresh()
        self.wd.wait_for_css("body")

        review_dom = self.wd.find_css(".review[review_id='%s']" % review.id)
        upvote = review_dom.find_element_by_class_name("upvote")
        downvote = review_dom.find_element_by_class_name("downvote")
        upvote_count = upvote.find_element_by_class_name("count")
        downvote_count = downvote.find_element_by_class_name("count")
        current_upvote_count = upvote_count.text
        current_downvote_count = downvote_count.text

        self.assertFalse(review_dom.find_element_by_class_name("deleted-message").is_displayed())
        upvote.click()
        self.assertTrue(review_dom.find_element_by_class_name("deleted-message").is_displayed())
        self.assertEqual(current_upvote_count, upvote_count.text)
        downvote.click()
        self.assertTrue(review_dom.find_element_by_class_name("deleted-message").is_displayed())
        self.assertEqual(current_downvote_count, downvote_count.text)
