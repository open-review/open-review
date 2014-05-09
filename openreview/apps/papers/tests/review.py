import time

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test import Client
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from openreview.apps.main.models import Review, Paper
from openreview.apps.tools.testing import create_test_user, create_test_review, SeleniumTestCase, create_test_paper, \
    assert_max_queries

__all__ = ["TestReviewView", "TestReviewView2", "TestReviewViewLive"]

class TestReviewView(TestCase):
    def test_n_queries_anonymous(self):
        """As an anonymous user, TestReview doesn't have to fetch owned reviews or votes."""
        paper = create_test_paper(n_reviews=1)

        with assert_max_queries(n=8):
            # [0] Paper
            # [1][2][3] Authors, keywords, categories (M2M relations)
            # [4] Review
            # [5] (Tree of) reviews
            # [6] Upvotes
            # [7] Downvotes
            Client().get(reverse("paper", args=[paper.id]))

class TestReviewView2(TestCase):
    """Running both n_queries test in the same TestCase somehow causes database queries
    to be cached. This should not happen, but I am not """
    def test_n_queries_logged_in(self):
        Paper.objects.all().delete()

        paper = create_test_paper(n_reviews=1)
        user = create_test_user(password="test")

        client = Client()
        client.login(username=user.username, password="test")

        with assert_max_queries(n=11):
            # [0-7] See test_n_queries_anonymous
            # [8] User
            # [9] Owned reviews
            # [10] Owned votes
            client.get(reverse("paper", args=[paper.id]))


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

        self.logout()
        self.open(reverse("paper", args=[r1.paper.id]))

        # Is 'you must be logged in to comment' displayed?
        self.wd.wait_for_css("body")

        review_dom = self.wd.find_css(".review[review_id='%s']" % r1.id)
        self.assertFalse(review_dom.find_element_by_class_name("login-message").is_displayed())
        review_dom.find_element_by_css_selector(".options .reply").click()
        self.assertTrue(review_dom.find_element_by_class_name("login-message").is_displayed())

    def test_writing_new(self):
        create_test_user(username="testdelete2", password="123")
        paper = create_test_paper()

        self.assertEqual(0, paper.reviews.count())

        self.login("testdelete2", "123")
        self.open(reverse("paper", args=[paper.id]))
        self.wd.wait_for_css("body")

        new = self.wd.find_css(".new")
        textarea = new.find_element_by_css_selector("textarea")
        textarea.send_keys("# Markdown\n")
        self.wd.wait_for_css(".preview h1")
        new.find_element_by_css_selector("[type=submit]").click()
        self.wd.wait_for_css("body")

        # Adding the review should fail, because the star rating is not set
        self.assertEqual(0, paper.reviews.count())

        # After setting the star rating, adding the review should succeed
        #time.sleep(60)
        self.wd.wait_for_css("div.starfield img")
        new = self.wd.find_css(".new")
        new.find_element_by_css_selector(".starfield img:nth-child(5)").click()
        self.wd.find_css(".new [type=submit]").click()
        self.wd.wait_for_css("body")
        self.assertEqual(1, paper.reviews.count())
        self.assertEqual(5, paper.reviews.all()[0].rating)

    def test_writing(self):
        user = create_test_user(username="writing", password="test")
        r1 = create_test_review(poster=user)
        self.login("writing", "test")

        self.open(reverse("paper", args=[r1.paper.id]))
        self.wd.wait_for_css("body")
        review_dom = self.wd.find_css(".review[review_id='%s']" % r1.id)

        review_dom.find_element_by_css_selector(".options .reply").click()
        new = review_dom.parent.find_element_by_css_selector(".new")
        preview = new.find_element_by_class_name("preview")
        textarea = new.find_element_by_css_selector("textarea")

        textarea.send_keys("# H1\n")
        textarea.send_keys("##H2\n")
        textarea.send_keys("*ooi* **oob**\n")
        textarea.send_keys("\n---------------------\n\n")
        textarea.send_keys("> quote\n\n")
        textarea.send_keys("    code\n\n")
        textarea.send_keys("Inline $e^x$ LaTex\n\n")
        textarea.send_keys("Not $$e^x$$ inline LaTex\n\n")
        text = textarea.get_attribute("value")

        self.wd.wait_for_css(".review-container .new .preview h1")
        h1 = preview.find_element_by_css_selector("h1")
        h2 = preview.find_element_by_css_selector("h2")
        em = preview.find_element_by_css_selector("em")
        strong = preview.find_element_by_css_selector("strong")
        hr = preview.find_element_by_css_selector("hr")
        quote = preview.find_element_by_css_selector("blockquote")
        code = preview.find_element_by_css_selector("pre")

        self.assertEqual(h1.text, "H1")
        self.assertEqual(h2.text, "H2")
        self.assertEqual(em.text, "ooi")
        self.assertEqual(strong.text, "oob")
        self.assertEqual(quote.text, "quote")
        self.assertEqual(code.text, "code")

        self.wd.wait_for_css(".MathJax")
        self.wd.wait_for_css(".MathJax_Display")
        self.assertEqual(1, len(preview.find_elements_by_css_selector(".MathJax_Display")))
        self.assertEqual(2, len(preview.find_elements_by_css_selector(".MathJax")))

        new.find_element_by_css_selector("[type=submit]").click()
        self.wd.wait_for_css("body")

        new_review = Review.objects.filter(poster=user, paper=r1.paper, parent=r1)
        self.assertTrue(len(new_review), 1)
        new_review = new_review[0]

        # Browser may insert \r upon submitting
        new_review_text = new_review.text.replace("\r", "")
        self.assertEqual(text.strip(), new_review_text.strip())

        # Should display error if user logged out without browser knowing
        self.wd.find_css("body").send_keys(Keys.CONTROL + 't')
        self.logout()
        self.wd.find_css("body").send_keys(Keys.CONTROL + 'w')

        # Give browser time to close tab
        time.sleep(0.3)

        review_dom = self.wd.find_css(".review[review_id='%s']" % new_review.id)
        review_dom.find_element_by_css_selector(".options .reply").click()

        # Waiting on :visible is not supported be Selenium :|
        time.sleep(0.5)

        review_dom.parent.find_element_by_css_selector(".preview-error").is_displayed()
