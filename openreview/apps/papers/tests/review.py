from django.core.urlresolvers import reverse
from django.test import Client
from django.utils.http import urlencode
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from openreview.apps.main.models import Paper, Review
from openreview.apps.tools.testing import create_test_user, create_test_review, SeleniumTestCase, create_test_paper, \
    BaseTestCase


class TestReviewView(BaseTestCase):
    def test_get(self):
        pass

    def test_patch(self):
        u1 = create_test_user(username="password", password="username")
        u2 = create_test_user(username="username", password="password")

        review = create_test_review(text="test123", poster=u2)

        url = reverse("review", args=[review.paper.id, review.id])

        # Not logged in
        c = Client()
        self.assertEqual(c.patch(url).status_code, 403)
        self.assertEqual(Review.objects.get(id=review.id).text, "test123")

        # Incorrect user
        c.login(username="password", password="username")
        self.assertEqual(c.patch(url).status_code, 403)
        self.assertEqual(Review.objects.get(id=review.id).text, "test123")

        # Correct user but missing 'text'
        c.login(username="username", password="password")
        self.assertEqual(c.patch(url).status_code, 400)
        self.assertEqual(Review.objects.get(id=review.id).text, "test123")

        # Non UTF-8 string
        self.assertEqual(c.patch(url, b"text=\x81").status_code, 400)
        self.assertEqual(Review.objects.get(id=review.id).text, "test123")

        # Correct request
        response = c.patch(url, urlencode(dict(text="foo123")))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.get(id=review.id).text, "foo123")

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

        paper = create_test_paper()
        review = create_test_review()

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
        url = reverse("review", args=[0, review.id])
        response = c.post(url, dict(text="foo"))
        self.assertEqual(404, response.status_code)

        # Review not found
        url = reverse("review", args=[paper.id, 0])
        response = c.post(url, dict(text="foo"))
        self.assertEqual(404, response.status_code)

        # Cannot create review with paper != given paper
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
