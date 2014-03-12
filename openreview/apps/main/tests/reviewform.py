from datetime import date
from unittest import TestCase

from django.core.urlresolvers import reverse

from openreview.apps.main.forms import PaperForm
from openreview.apps.tools.testing import SeleniumTestCase, create_test_keyword, assert_max_queries
from openreview.apps.tools.testing import create_test_author, create_test_user
from openreview.apps.main.models import Paper, Review


__all__ = ["TestReviewForm", "TestReviewFormLive"]

class TestReviewForm(TestCase):
    def test_paper_form(self):
        test_data = {
            "type": "manually",
            "authors": "Jean\nPiere",
            "title": "test-title",
            "abstract": "foo",
            "doc_id": "arXiv:1403.0438",
            "keywords": "a,b"
        }

        form = PaperForm(data=test_data)
        self.assertTrue(form.is_valid())
        self.assertEqual({"Jean", "Piere"}, {a.name for a in form.cleaned_data["authors"]})
        self.assertEqual({"a", "b"}, {k.label for k in form.cleaned_data["keywords"]})

        # Test whitespace characters
        form = PaperForm(data=dict(test_data, **{
            "authors": "\t\t\n  \n Jean\t\n\rPiere\n",
            "keywords": "\t\t\n  \n a\t,\n\rb\n"
        }))

        self.assertTrue(form.is_valid())
        self.assertEqual({"Jean", "Piere"}, {a.name for a in form.cleaned_data["authors"]})
        self.assertEqual({"a", "b"}, {k.label for k in form.cleaned_data["keywords"]})

        # Form must not create new database entries if keywords/authors already present
        author = create_test_author(name="Jean")
        keyword = create_test_keyword(label="a")
        form = PaperForm(data=test_data)
        self.assertTrue(form.is_valid())

        jean = form.cleaned_data["authors"][0]
        piere = form.cleaned_data["authors"][1]
        self.assertIsNotNone(jean.id)
        self.assertIsNone(piere.id)

        a = form.cleaned_data["keywords"][0]
        b = form.cleaned_data["keywords"][1]
        self.assertIsNotNone(a.id)
        self.assertIsNone(b.id)

        # save(commit=False) should not save authors/keywords
        with assert_max_queries(n=0):
            form.save(commit=False)
        self.assertIsNotNone(jean.id)
        self.assertIsNone(piere.id)
        self.assertIsNotNone(a.id)
        self.assertIsNone(b.id)

        # save(commit=True) should
        with assert_max_queries(n=7):
            # Django queries database before inserting to make sure it doesn't include duplicates
            # [1] Saving paper
            # [2] INSERT piere
            # [3] SELECT authors
            # [4] INSERT authors
            # [5] INSERT b
            # [6] SELECT keywords
            # [7] INSERT keywords
            paper = form.save(commit=True)
        self.assertIsNotNone(jean.id)
        self.assertIsNotNone(piere.id)
        self.assertIsNotNone(a.id)
        self.assertIsNotNone(b.id)

        self.assertEqual(set([jean, piere]), set(paper.authors.all()))
        self.assertEqual(set([a, b]), set(paper.keywords.all()))


class TestReviewFormLive(SeleniumTestCase):
    def setUp(self):
        self.a = create_test_author(name="tester")
        self.u = create_test_user()
        super().setUp()

    def test_paper_gets_committed(self):
        self.open(reverse("add_review"))
        # Check if redirected to login if not logged in
        self.assertTrue(self.wd.current_url.endswith(
            "{login}?next={next}".format(login=reverse("accounts-login"), next=reverse("add_review"))))
        self.wd.wait_for_css("body")
        self.wd.find_css("#id_login_username").send_keys(self.u.username)
        self.wd.find_css("#id_login_password").send_keys("test")
        self.wd.find_css('input[value="Login"]').click()
        # Check if on the right page now
        self.assertFalse(reverse("accounts-login") in self.wd.current_url)
        self.assertTrue(self.wd.current_url.endswith(reverse("add_review")))
        self.wd.wait_for_css("#id_title")

        # Select the right paper
        self.wd.find_css("#id_type option[value=\"manually\"]").click()
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
        self.assertEqual(p.doc_id, "1403.0438")
        #self.assertEqual(p.publish_date, "Jéan-Pièrre van 't Hoff")
        self.assertEqual(p.abstract, "This paper is fancy.")
        self.assertEqual(p.publish_date, date(2012, 1, 1))
        self.assertEqual(p.publisher, "Springer")
        self.assertEqual(p.urls, "http://example.org/document.pdf")

        self.assertTrue(Review.objects.count() == 1)
        r = Review.objects.get(paper=p.id)
        self.assertEqual(r.poster, self.u)
        self.assertEqual(r.text.replace("\r", ""), "test\nlol\ndoei")