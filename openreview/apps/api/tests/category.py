from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from openreview.apps.api.tests.review import _get_json
from openreview.apps.main.models import Category
from openreview.apps.tools.testing import create_test_category, create_test_user

__all__ = ["TestCategoryAPI"]

class TestCategoryAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username=create_test_user(password="test"), password="test")

    def test_list(self):
        category = create_test_category()
        self.assertEqual(1, Category.objects.count())

        _, content = _get_json(reverse("category-list"))
        self.assertEqual(1, content["count"])
        self.assertEqual(category.name, content["results"][0]["name"])
        self.assertEqual(category.arxiv_code, content["results"][0]["arxiv_code"])
        self.assertEqual(category.parent, content["results"][0]["parent"])

    def test_post(self):
        """Categories can online be added by openreview (fixtures) itself."""
        response = self.client.post(reverse("category-list"))
        self.assertEqual(response.status_code, 405, "POST should not be allowed (405 = METHOD NOT ALLOWED)")

    def test_put(self):
        response = self.client.put(reverse("category-list"))
        self.assertEqual(response.status_code, 405, "PUT should not be allowed (405 = METHOD NOT ALLOWED)")

    def test_patch(self):
        response = self.client.patch(reverse("category-list"))
        self.assertEqual(response.status_code, 405, "PATCH should not be allowed (405 = METHOD NOT ALLOWED)")

    def test_delete(self):
        response = self.client.patch(reverse("category-list"))
        self.assertEqual(response.status_code, 405, "DELETE should not be allowed (405 = METHOD NOT ALLOWED)")
