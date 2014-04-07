from datetime import date
import os
from unittest import TestCase
from django.core.management import call_command

from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.core import management
from django.test.client import Client

from openreview.apps.main.forms import PaperForm
from openreview.apps.tools.testing import SeleniumTestCase, create_test_keyword, assert_max_queries
from openreview.apps.tools.testing import create_test_author, create_test_user
from openreview.apps.main.models import Paper, Review, Vote, Category

from openreview.apps.papers import scrapers


__all__ = ["TestReviewForm", "TestReviewFormLive"]


class TestReviewForm(TestCase):
    def setUp(self):
        call_command("loaddata", "initial_data")

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

        # save(commit=False) should not save authors/keywords,
        # but should only check for existing entries
        with assert_max_queries(n=1):
            form.save(commit=False)
        self.assertIsNotNone(jean.id)
        self.assertIsNone(piere.id)
        self.assertIsNotNone(a.id)
        self.assertIsNone(b.id)

        # save(commit=True) should
        with assert_max_queries(n=9):
            # Django queries database before inserting to make sure it doesn't include duplicates
            # [0] Checkout for duplicate Paper entry
            # [1] Saving paper
            # [2] INSERT piere
            # [3] SELECT authors
            # [4] INSERT authors
            # [5] INSERT b
            # [6] SELECT keywords
            # [7] INSERT keywords
            # [8] SELECT categories         
            paper = form.save(commit=True)
        self.assertIsNotNone(jean.id)
        self.assertIsNotNone(piere.id)
        self.assertIsNotNone(a.id)
        self.assertIsNotNone(b.id)

        self.assertEqual(set([jean, piere]), set(paper.authors.all()))
        self.assertEqual(set([a, b]), set(paper.keywords.all()))

    def test_no_duplicate_papers(self):
        test_data = {
            "type": "manually",
            "authors": "Jantje",
            "title": "test-title",
            "abstract": "foo",
            "doc_id": "1403.0438"
        }

        p = PaperForm(data=test_data)
        self.assertTrue(p.is_valid())
        with assert_max_queries(n=6):
            p.save(commit=True)

        with assert_max_queries(n=1):
            # This should only return de existing database entry!
            p.save(commit=True)

    def test_form_filled_in_automatically(self):
        cache.clear()
        c = Client()
        scrapers.urlopen = lambda x: open(os.path.dirname(os.path.realpath(__file__)) +
                                          "/../../papers/testfiles/1306.3879.xml")
        user = create_test_user()
        c.post(reverse("accounts-login"), {'username': user.username, 'password': "test", 'existing': "Login"})
        c.post(reverse("add_review"), {'type': "arxiv", 'doc_id': "1306.3879", 'text': "Just nutin",
                                       'add_review': "Submit", 'rating': 5})

        # An item in de db for this paper should now exist
        p = Paper.objects.get(doc_id="1306.3879")
        self.assertEqual(p.title, """Chandra View of the Ultra-Steep Spectrum Radio Source in Abell 2443:
  Merger Shock-Induced Compression of Fossil Radio Plasma?""")
        self.assertEqual([a.name for a in p.authors.all()], ['T. E. Clarke', 'S. W. Randall', 'C. L. Sarazin',
                                                             'E. L. Blanton', 'S. Giacintucci'])
        self.assertEqual(p.urls, "http://arxiv.org/abs/1306.3879v1")
        self.assertEqual(p.abstract, """  We present a new Chandra X-ray observation of the intracluster medium in the
galaxy cluster Abell 2443, hosting an ultra-steep spectrum radio source. The
data reveal that the intracluster medium is highly disturbed. The thermal gas
in the core is elongated along a northwest to southeast axis and there is a
cool tail to the north. We also detect two X-ray surface brightness edges near
the cluster core. The edges appear to be consistent with an inner cold front to
the northeast of the core and an outer shock front to the southeast of the
core. The southeastern edge is coincident with the location of the radio relic
as expected for shock (re)acceleration or adiabatic compression of fossil
relativistic electrons.\n""")
        self.assertEqual([c.arxiv_code for c in p.categories.all()], ["astro-ph.CO"])


class TestReviewFormLive(SeleniumTestCase):
    def setUp(self):
        self.a = create_test_author(name="tester")
        self.u = create_test_user()
        super().setUp()

    def test_paper_gets_committed(self):
        Vote.objects.all().delete()
        Review.objects.all().delete()
        self.assertEqual(Review.objects.count(), 0)
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
        self.wd.find_css('#id_type option[value="manually"]').click()
        self.wd.find_css("#id_title").send_keys("Some fancy paper title")
        self.wd.find_css("#id_doc_id").send_keys("1403.04385")
        self.wd.find_css("#id_authors").send_keys("Jéan-Pièrre van 't Hoff")
        self.wd.find_css("#id_keywords").send_keys("Aa,Bb,Cc")
        self.wd.find_css("#id_abstract").send_keys("This paper is fancy.")
        self.wd.find_css("#id_publish_date").send_keys("2012-01-01")
        self.wd.find_css("#id_publisher").send_keys("Springer")
        self.wd.find_css("#id_urls").send_keys("http://example.org/document.pdf")
        self.wd.find_css("#id_text").send_keys("test\nlol\ndoei")

        catlist = self.wd.find_css("#id_categories")
        for option in catlist.find_elements_by_tag_name('option'):
            if option.text == 'Artificial Intelligence':
                option.click()

        self.wd.wait_for_css("div.starfield img")
        new = self.wd.find_css(".new")
        new.find_element_by_css_selector(".starfield img:nth-child(5)").click()
        self.wd.find_css("input[name=\"add_review\"]").click()
        self.wd.wait_for_css("body")

        # Review is saved well
        p = Paper.objects.get(title="Some fancy paper title")
        self.assertEqual(p.doc_id, "1403.04385")
        self.assertEqual([a.name for a in p.authors.all()], ["Jéan-Pièrre van 't Hoff"])
        self.assertEqual([c.name for c in p.categories.all()], ["Artificial Intelligence"])
        self.assertEqual([k.label for k in p.keywords.all()], ["Aa","Bb","Cc"])
        self.assertEqual(p.abstract, "This paper is fancy.")
        self.assertEqual(p.publish_date, date(2012, 1, 1))
        self.assertEqual(p.publisher, "Springer")
        self.assertEqual(p.urls, "http://example.org/document.pdf")

        self.assertEqual(Review.objects.count(), 1)
        r = Review.objects.get(paper=p.id)
        self.assertEqual(r.poster, self.u)
        self.assertEqual(r.text.replace("\r", ""), "test\nlol\ndoei")
