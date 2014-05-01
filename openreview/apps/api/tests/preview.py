from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from openreview.apps.api.tests.review import _get_json
from openreview.apps.tools.testing import create_test_user, create_test_paper


class PreviewProcedureTest(TestCase):
    def setUp(self):
        self.user = create_test_user(password="test")
        self.client = Client()
        self.client.login(username=self.user.username, password="test")

    @property
    def url(self):
        return reverse("procedure-preview")

    def test_get(self):
        response = Client().get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"details": "POST only."}')

    def test_anonymous_post(self):
        response = Client().post(self.url)
        self.assertEqual(response.status_code, 403, "Anonymous users cannot post.")

    def test_missing_fields_post(self):
        response, content = _get_json(self.url, data={}, client=self.client)
        self.assertEqual(response.status_code, 400)

        for field in ['rating', 'visibility', 'text', 'paper']:
            self.assertEqual(content['details'][field], ["This field is required."])

    def test_post(self):
        data = dict(text="# H1", rating=2, visibility="semi_anonymous", paper=create_test_paper().id)
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertFalse(self.user.username in content)
        self.assertTrue("<h1>H1</h1>" in content)

        data["visibility"] = "public"
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertTrue("<h1>H1</h1>" in content)
        self.assertTrue(self.user.username in content)
