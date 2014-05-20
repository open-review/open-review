from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test import Client

from openreview.apps.main.models import Review, Paper
from openreview.apps.tools.testing import create_test_user, create_test_review, SeleniumTestCase, create_test_paper, \
    assert_max_queries

__all__ = ["TestReviewView", "TestReviewView2", "TestReviewViewLive"]


class TestReviewView(TestCase):
    def test_n_queries_anonymous(self):
        """As an anonymous user, TestReview doesn't have to fetch owned reviews or votes."""
        paper = create_test_paper(n_reviews=1)

        with assert_max_queries(n=11):
            # [0] Paper
            # [1][2][3] Authors, keywords, categories (M2M relations)
            # [4] Review
            # [5] (Tree of) reviews
            # [6] Upvotes
            # [7] Downvotes
            # [8][9][10] Authors, keywords, categories (fetching data)
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

        with assert_max_queries(n=14):
            # [0-10] See test_n_queries_anonymous
            # [9] User
            # [10] Owned reviews
            # [11] Owned votes
            client.get(reverse("paper", args=[paper.id]))


class TestReviewViewLive(SeleniumTestCase):
    def setUp(self):
        """
        Create a paper with one review of `self.user` and one of another user.
        """
        self.user = create_test_user()
        self.review1 = create_test_review(poster=self.user)
        self.paper = self.review1.paper
        self.review2 = create_test_review(paper=self.paper)
        self.open(reverse("paper", args=[self.paper.id]))

    def _write_test_text(self, textarea):
        textarea.send_keys("# H1\n")
        textarea.send_keys("##H2\n")
        textarea.send_keys("*ooi* **oob**\n")
        textarea.send_keys("\n---------------------\n\n")
        textarea.send_keys("> quote\n\n")
        textarea.send_keys("    code\n\n")
        textarea.send_keys("Inline $e^x$ LaTex\n\n")
        textarea.send_keys("Not $$e^x$$ inline LaTex\n\n")

    def _test_preview_text(self, preview):
        h1 = preview.find_element_by_css_selector("h1")
        self.assertEqual(h1.text, "H1")

        h2 = preview.find_element_by_css_selector("h2")
        self.assertEqual(h2.text, "H2")

        em = preview.find_element_by_css_selector("em")
        self.assertEqual(em.text, "ooi")

        strong = preview.find_element_by_css_selector("strong")
        self.assertEqual(strong.text, "oob")

        quote = preview.find_element_by_css_selector("blockquote")
        self.assertEqual(quote.text, "quote")

        code = preview.find_element_by_css_selector("pre")
        self.assertEqual(code.text, "code")

        # Horizontal line should be present due to '--------'.
        hr = preview.find_element_by_css_selector("hr")

    def test_anonymous(self):
        """No reply, edit or delete buttons should show if we're anonymous."""
        for button in ("edit", "reply", "delete"):
            for button_element in self.wd.find_css(".options .%s" % button):
                self.assertFalse(button_element.is_displayed())

    def test_reply(self):
        self.login(self.user.username)

        # Setup DOM elements
        owned_review = self.wd.find_css('[data-review-id="%s"]' % self.review1.id)
        owned_review_container = owned_review.parent
        reply_section = owned_review_container.find_element_by_css_selector('#reply-to-%s' % self.review1.id)
        preview_section = owned_review_container.find_element_by_css_selector('#preview-of-reply-%s' % self.review1.id)
#
        # Test whether buttons are displayed, and sections are hidden
        reply_button = owned_review.find_element_by_css_selector(".options .reply")
        self.assertTrue(reply_button.is_displayed(), "Edit button should be visible on owned review")
        self.assertFalse(reply_section.is_displayed(), "Reply section should not be visible if edit button was not clicked.")

        # Open writing area!
        reply_button.click()
        self.assertTrue(reply_button.is_displayed(), "Edit button should be visible on owned review")
        self.assertTrue(reply_section.is_displayed(), "Reply section should be visible if edit button was clicked.")

        # Does clicking on reply again close edit area?
        reply_button.click()
        self.assertTrue(reply_button.is_displayed(), "Edit button should be visible on owned review")
        self.assertFalse(reply_section.is_displayed(), "Reply section should not be visible if edit button was not clicked.")
        self.assertFalse(preview_section.is_displayed(), "Preview section should not be visible after closing edit section.")

        # Reopen area
        reply_button.click()

        # Test markdown, latex, etc.
        self._write_test_text(reply_section.find_element_by_css_selector("textarea"))
        self.wd.wait_for_css(".preview article h1")
        self.assertTrue(preview_section.is_displayed(), "Preview section should be visible if edit button was clicked.")
        self._test_preview_text(preview_section)

        # Test submit.
        self.assertFalse(Review.objects.filter(parent=self.review1.id).exists())
        reply_section.find_element_by_css_selector('[type="submit"]').click()
        self.wait_for_model(Review, parent=self.review1.id)

        reply = Review.objects.get(parent=self.review1.id)
        self.assertEqual(reply.poster, self.user)

    def test_delete(self):
        self.login(self.user.username)

        self.assertFalse(Review.objects.filter(text=None))

        owned_review = self.wd.find_css('[data-review-id="%s"]' % self.review1.id)
        delete_button = owned_review.find_element_by_css_selector(".options .delete")
        delete_button.click()

        self.wait_for_model(Review, text=None)

    def test_edit(self):
        # Replying uses same codepaths as replying, so we will not test extensively here.
        self.login(self.user.username)

        # Setup DOM elements
        owned_review = self.wd.find_css('[data-review-id="%s"]' % self.review1.id)
        owned_review_container = owned_review.parent
        edit_section = owned_review_container.find_element_by_css_selector('#edit-%s' % self.review1.id)
        preview_section = owned_review_container.find_element_by_css_selector('#preview-of-edit-%s' % self.review1.id)
        edit_button = owned_review.find_element_by_css_selector(".options .edit")

        # Open editing area
        edit_button.click()

        # Test markdown, latex, etc.
        textarea = edit_section.find_element_by_css_selector("textarea")
        self._write_test_text(textarea)
        self.wd.wait_for_css(".preview article h1")
        self._test_preview_text(preview_section)

        # Test submit.
        self.assertFalse(Review.objects.filter(text="a"))
        textarea.clear()
        textarea.send_keys("a")
        edit_section.find_element_by_css_selector('[type="submit"]').click()
        self.wait_for_model(Review, text="a")
