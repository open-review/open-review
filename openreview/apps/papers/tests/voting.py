from django.core.urlresolvers import reverse
from selenium.common.exceptions import NoSuchElementException

from openreview.apps.main.models import Vote
from openreview.apps.tools.testing import SeleniumTestCase, create_test_paper, create_test_user


__all__ = ["TestVoteViewLive"]

class TestVoteViewLive(SeleniumTestCase):
    def setUp(self):
        self.paper = create_test_paper(n_reviews=2)
        self.review = self.paper.reviews.all()[0]
        self.open(reverse("paper", args=[self.paper.id]))
        self.wd.wait_for_css("body")

    def test_anonymous(self):
        """Do we display a message if we're trying to vote as an anonymous user?"""
        self.assertRaises(NoSuchElementException, self.wd.find_css, ".review .login-message :visible")
        self.assertRaises(NoSuchElementException, self.wd.find_css, ".review .login-message:visible")

        self.assertEqual(
            2, len(self.wd.find_css(".review .login-message")),
            msg="Login message boxes must be in DOM, but not yet visible.")

        # Click on upvote button: is error displayed?
        review_dom = self.wd.find_css('.review[data-review-id="%s"]' % self.review.id)
        review_dom.find_element_by_css_selector(".voting .up").click()
        self.assertTrue(review_dom.find_element_by_class_name("login-message").is_displayed())

    def test_deleted(self):
        """Do we display a message if we're trying to vote on a deleted review?"""
        # Delete review
        self.review.delete()

        # Login
        user = create_test_user()
        self.login(username=user.username)
        self.open(reverse("paper", args=[self.paper.id]))

        # Click upvote button: is error displayed?
        self.assertRaises(NoSuchElementException, self.wd.find_css, ".review .deleted-message :visible")
        self.assertRaises(NoSuchElementException, self.wd.find_css, ".review .deleted-message:visible")

        self.assertEqual(
            2, len(self.wd.find_css(".review .deleted-message")),
            msg="Login message boxes must be in DOM, but not yet visible.")

        # Click on upvote button: is error displayed?
        review_dom = self.wd.find_css('.review[data-review-id="%s"]' % self.review.id)
        review_dom.find_element_by_css_selector(".voting .up").click()
        self.assertTrue(review_dom.find_element_by_class_name("deleted-message").is_displayed())


    def test_voting(self):
        """Test voting by a) monitoring database b) watching counters"""
        # Login
        user = create_test_user()
        self.login(username=user.username)
        self.open(reverse("paper", args=[self.paper.id]))

        review_dom = self.wd.find_css('.review[data-review-id="%s"]' % self.review.id)
        upvote = review_dom.find_element_by_class_name("up")
        downvote = review_dom.find_element_by_class_name("down")
        counter = review_dom.find_element_by_class_name("counter")

        # Test default = 0
        self.assertEqual("0", counter.text)
        self.assertFalse(Vote.objects.filter(voter=user, review=self.review).exists())

        # Test upvote
        upvote.click()
        self.assertEqual("1", counter.text)
        self.wait_for_model(Vote, review=self.review, voter=user, vote=1)

        # Test upvote --> downvote
        downvote.click()
        self.assertEqual("-1", counter.text)
        self.wait_for_model(Vote, review=self.review, voter=user, vote=-1)

        # Test neutral vote (clicking downvote *again*)
        downvote.click()
        self.assertEqual("0", counter.text)
        self.wait_for_model(Vote, review=self.review, voter=user, vote=0)
