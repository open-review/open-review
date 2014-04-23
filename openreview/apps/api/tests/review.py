import json
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from openreview.apps.main.models import Review
from openreview.apps.tools.testing import create_test_review, create_test_user, create_test_paper

__all__ = ["TestReviewAPI"]

def _get_json(url, client=None, data=None, encoding="utf-8"):
    client = client or Client()
    if data is None:
        response = client.get(url)
    else:
        response = client.post(url, json.dumps(data), content_type="application/json")
    return response, json.loads(response.content.decode(encoding))

def _patch(url, data=None, client=None):
    data = data or {}
    client = client or Client()
    return client.patch(url, data=json.dumps(data), content_type="application/json")

class TestReviewAPI(TestCase):
    def setUp(self):
        Review.objects.all().delete()

    def test_list(self):
        """Test basic listing of reviews. Is count correct, pagination available, etc."""
        r1 = create_test_review(text="foo")
        r2 = create_test_review(text="bar")

        _, content = _get_json(reverse("review-list"))
        self.assertEqual(content["count"], 2, "2 reviews should be in database")
        self.assertEqual(len(content["results"]), 2, "2 reviews should be in database")
        self.assertEqual(content["next"], None, "Default paging is per_page=10, so all reviews should be displayed")
        self.assertEqual(content["previous"], None, "Default paging is per_page=10, so all reviews should be displayed")

        r = content["results"][0]
        self.assertIn(r["id"], [r1.id, r2.id])
        self.assertIn(r["text"], ["foo", "bar"])

        # Get r1 from json
        if r["id"] != r1.id:
            r = content["results"][1]

        self.assertTrue(r["url"].endswith("/api/v1/reviews/{r1.id}/".format(**locals())))
        self.assertTrue(r["poster"].endswith("/api/v1/users/{r1.poster_id}/".format(**locals())))
        self.assertTrue(r["paper"].endswith("/api/v1/papers/{r1.paper_id}/".format(**locals())))

    def test_hiding(self):
        """Anonymous reviews should not display their poster."""
        r1 = create_test_review()
        r1.set_semi_anonymous()
        r1.save()

        self.assertTrue(r1.is_semi_anonymous)
        self.assertIsNotNone(r1.poster, "Poster should be None in order for this test to be of use.")

        _, content = _get_json(reverse("review-list"))
        r = content["results"][0]
        self.assertEqual(content["count"], 1, "1 review should be in database")
        self.assertIsNone(r["poster"], "Review is semi anonymous, poster should be hidden")

        _, r = _get_json(reverse("review-detail", args=[r1.id]))
        self.assertIsNone(r["poster"], "Review is semi anonymous, poster should be hidden")

        # If user is logged and a review is its own, `poster` should be displayed
        r1.poster.set_password("test")
        r1.save()
        client = Client()
        client.login(username=r1.poster.username, password="test")

        _, r = _get_json(reverse("review-detail", args=[r1.id]), client=client)
        self.assertTrue(r["poster"].endswith("/{r1.poster_id}/".format(r1=r1)),
                        "Review owned by logged in user: poster should be visible.")

        # User shouldn't be able to see others
        r2 = create_test_review()
        r2.set_semi_anonymous()
        r2.save()
        _, r = _get_json(reverse("review-detail", args=[r2.id]), client=client)
        self.assertIsNone(r["poster"], "Review is semi anonymous, logged in user is not owner")

    def test_delete(self):
        r1 = create_test_review(poster=create_test_user(password="test"))

        c = Client()
        response = c.delete(reverse("review-detail", args=[r1.id]))
        self.assertFalse(Review.objects.get(id=r1.id).is_deleted)
        self.assertEqual(response.status_code, 403, "Deleting as non-owner should raise PermissionDenied")

        u = create_test_user(password="test")
        c.login(username=u.username, password="test")
        response = c.delete(reverse("review-detail", args=[r1.id]))
        self.assertFalse(Review.objects.get(id=r1.id).is_deleted)
        self.assertEqual(response.status_code, 403, "Deleting as non-owner should raise PermissionDenied")

        c.login(username=r1.poster.username, password="test")
        response = c.delete(reverse("review-detail", args=[r1.id]))
        self.assertTrue(Review.objects.get(id=r1.id).is_deleted)
        self.assertEqual(response.status_code, 204, "Deleting as owner should be OK")

    def test_patch(self):
        r1 = create_test_review(poster=create_test_user(password="test"), rating=2)
        url = reverse("review-detail", args=[r1.id])

        response = _patch(url)
        self.assertEqual(response.status_code, 403, "Changing as non-owner should raise PermissionDenied")

        # Patch 'text' should result in only the `text` property to be changed
        c = Client()
        c.login(username=r1.poster.username, password="test")
        response = _patch(url, {"text": "testpatch"}, client=c)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.get(id=r1.id).text, "testpatch")
        self.assertEqual(Review.objects.get(id=r1.id).rating, 2)

        # We should not be able to push invalid values
        response = _patch(url, {"anonymous": False, "external": True}, client=c)
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["detail"], "External reviews must be anonymous.")

        # We should not be able to change parents
        r2 = create_test_review(paper=r1.paper)
        response = _patch(url, {"parent": r2.id}, client=c)
        self.assertEqual(response.status_code, 403, "We must not be able to change parents.")

    def test_post(self):
        url = reverse("review-list")

        response, _ = _get_json(url, data={})
        self.assertEqual(response.status_code, 403, "User should be logged in.")

        # Test bad request (forget to include all fields)
        u = create_test_user(password="test")
        client = Client()
        client.login(username=u.username, password="test")
        response, content = _get_json(url, data={}, client=client)

        for field in ["poster", "paper", "rating"]:
            self.assertEqual(content[field][0], "This field is required.")

        # Forget 'text'
        paper = create_test_paper()
        data = dict(poster=u.id, paper=paper.id, rating=2)
        response, content = _get_json(url, data=data, client=client)
        self.assertEqual(response.status_code, 403, "New review should contain text.")

        # Can we create a new review?
        data["text"] = "BOE!"
        response, content = _get_json(url, data=data, client=client)
        self.assertEqual(response.status_code, 201)
        review = Review.objects.filter(paper=paper, poster=u.id, rating=2)
        self.assertTrue(review.exists())
        self.assertEqual(review[0].text, "BOE!")

        # Can we create a comment?
        data["parent"] = review[0].id
        data["text"] = "comment"
        response, content = _get_json(url, data=data, client=client)
        self.assertEqual(response.status_code, 201)
        review = Review.objects.filter(paper=paper, poster=u.id, rating=2, parent=review[0])
        self.assertTrue(review.exists())
        self.assertEqual(review[0].text, "comment")

