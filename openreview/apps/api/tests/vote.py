from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from openreview.apps.api.tests.review import _get_json
from openreview.apps.main.models import Vote
from openreview.apps.tools.testing import create_test_user, create_test_review


__all__ = ["VoteProcedureTest"]


class VoteProcedureTest(TestCase):
    def setUp(self):
        self.user = create_test_user(password="test")
        self.client = Client()
        self.client.login(username=self.user.username, password="test")

    @property
    def url(self):
        return reverse("procedure-vote")

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

        for field in ['vote', 'review']:
            self.assertEqual(content['details'][field], ["This field is required."])

    def test_post(self):
        review = create_test_review()
        data = dict(vote=1, review=review.id)
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, b'{"details": "OK"}')
        self.assertTrue(Vote.objects.filter(review=review, vote=1, voter=self.user))

    def test_overwrite(self):
        review = create_test_review()
        Vote.objects.create(voter=self.user, vote=1, review=review)

        data = dict(vote=-1, review=review.id)
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, b'{"details": "OK"}')
        self.assertTrue(Vote.objects.filter(review=review, vote=-1, voter=self.user))
