from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from openreview.apps.api.tests.review import _get_json
from openreview.apps.main.models import Paper
from openreview.apps.tools.testing import create_test_paper, create_test_user, create_test_category, create_test_author, \
    create_test_keyword


__all__ = ["TestPaperAPI"]

class TestPaperAPI(TestCase):
    url = reverse("paper-list")

    def setUp(self):
        Paper.objects.all().delete()
        self.client = Client()
        self.client.login(username=create_test_user(password="test").username, password="test")
        self.data = {
            "title": "foo",
            "abstract": "bar",
            "authors": [],
            "categories": [],
            "keywords": []
        }

    def test_fetch(self):
        paper = create_test_paper(n_authors=1, n_keywords=2, n_categories=3)

        author = paper.authors.all()[0]
        author.user = create_test_user()
        author.save()

        _, content = _get_json(self.url)
        self.assertEqual(content["count"], 1)
        self.assertEqual(len(content["results"][0]["authors"]), 1)
        self.assertEqual(len(content["results"][0]["keywords"]), 2)
        self.assertEqual(len(content["results"][0]["categories"]), 3)
        self.assertTrue(content["results"][0]["authors"][0].startswith("http://testserver/"))

        _, content = _get_json(self.url + "?hyperlinks=False")
        authors = {a.pk for a in paper.authors.all()}
        keywords = {a.pk for a in paper.keywords.all()}
        categories = {a.pk for a in paper.categories.all()}
        self.assertEqual(set(content["results"][0]["authors"]), authors)
        self.assertEqual(set(content["results"][0]["keywords"]), keywords)
        self.assertEqual(set(content["results"][0]["categories"]), categories)

    def test_post_anonymous(self):
        response, _ = _get_json(self.url, data={})
        self.assertEqual(response.status_code, 403, "Anonymous users should not be able to create papers (FORBIDDEN)")

    def test_post_missing_data(self):
        client = Client()
        client.login(username=create_test_user(password="test").username, password="test")
        response, content = _get_json(self.url, data={}, client=client)
        self.assertEqual(response.status_code, 400, "Data must be provided.")

        for field_name in ["title", "abstract"]:
            self.assertEqual(content[field_name], ["This field is required."])

        for field_name in ["authors", "keywords", "categories"]:
            self.assertTrue(field_name not in content)

    def test_post_empty_paper(self):
        response, content = _get_json(self.url, data=self.data, client=self.client)
        self.assertEqual(response.status_code, 201, "Adding empty paper failed.")
        self.assertEqual(content["title"], "foo")
        self.assertEqual(content["abstract"], "bar")
        self.assertTrue(Paper.objects.filter(id=content["id"]).exists())

    def test_post_add_paper(self):
        self.assertEqual(0, Paper.objects.count(), "Papers must not exist for this test to finish.")

        a1, a2 = create_test_author(), create_test_author()
        k1, k2 = create_test_keyword(), create_test_keyword()
        c1, c2 = create_test_category(), create_test_category()

        self.data["authors"].append(a1.id)
        self.data["keywords"].append(k1.id)
        self.data["categories"].append(c1.id)

        response, content = _get_json(self.url, data=self.data, client=self.client)
        self.assertEqual(201, response.status_code)

        paper = Paper.objects.all()
        self.assertTrue(paper.exists(), "Paper should be created after API call.")
        self.assertEqual(set(paper[0].authors.all()), {a1})
        self.assertEqual(set(paper[0].keywords.all()), {k1})
        self.assertEqual(set(paper[0].categories.all()), {c1})
