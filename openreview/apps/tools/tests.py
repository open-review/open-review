import io
import os
import unittest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import RequestFactory
from django.views.generic import View
import sys
from openreview.apps.main.models import Paper
from openreview.apps.tools.auth import login_required
from openreview.apps.tools.string import get_bool
from openreview.apps.tools.testing import list_queries, assert_max_queries, create_test_user, create_test_review
from openreview.apps.tools.views import ModelViewMixin

__all__ = ["TestTesting", "TestModelViewMixin", "TestAuth", "TestString"]

class TestString(unittest.TestCase):
    def _test_get_bool(self):

        os.environ.update({
            "negative1": "0",
            "negative2": "False",
            "negative3": "false",
            "negative4": "faLse",
            "negative5": " \n  false\n\n \n\t",
            "positive1": "1",
            "positive2": "True",
            "illegal": "foo"
        })

        self.assertFalse(get_bool("negative1"))
        self.assertFalse(get_bool("negative2"))
        self.assertFalse(get_bool("negative3"))
        self.assertFalse(get_bool("negative4"))
        self.assertFalse(get_bool("negative5"))
        self.assertTrue(get_bool("positive1"))
        self.assertTrue(get_bool("positive2"))

        self.assertRaises(ValueError, get_bool, "illegal")

        self.assertEqual(get_bool("non-existent"), None)
        self.assertEqual(get_bool("non-existent", default=False), False)

        self.assertRaises(ValueError, get_bool, "non-existent", err_empty=True)

    def test_get_bool(self):
        # Save and restore environment variables
        environ = os.environ.copy()
        os.environ.clear()

        # Supress stupid printing of error messages
        actualstdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            self._test_get_bool()
        finally:
            os.environ.update(environ)
            sys.stdout = actualstdout

class TestAuth(unittest.TestCase):
    def test_login_required(self):
        @login_required
        def test1(request):
            return "s"

        @login_required()
        def test2(request):
            return "s"

        @login_required(raise_exception=True)
        def test3(request):
            return "s"

        @login_required(login_url="/foo2/")
        def test4(request):
            return "s"

        request = RequestFactory().get("/redirect/")
        request.user = AnonymousUser()

        self.assertEqual(test1(request).status_code, 302)
        self.assertEqual(test2(request).status_code, 302)
        self.assertRaises(PermissionDenied, test3, request)
        self.assertEqual(test4(request).url, "/foo2/?next=/redirect/")

        request.user = create_test_user()
        self.assertEqual(test1(request), "s")
        self.assertEqual(test2(request), "s")
        self.assertEqual(test3(request), "s")
        self.assertEqual(test4(request), "s")


class TestView(ModelViewMixin, View):
    def dispatch(self, request, *args, **kwargs):
        return self

class TestModelViewMixin(unittest.TestCase):
    def test_manager(self):
        user = create_test_user()
        review = create_test_review()
        view = TestView.as_view()(None, paper_id=-1, user_id=user.id, review_id=review.id)

        self.assertTrue(hasattr(view, "objects"))
        self.assertRaises(Http404, lambda: view.objects.paper)
        self.assertRaises(Http404, view.objects.get_paper)
        self.assertRaises(AttributeError, lambda: view.objects.foo)
        self.assertRaises(AttributeError, lambda: view.objects.get_foo)
        self.assertRaises(AttributeError, lambda: view.objects.get_)
        self.assertRaises(KeyError, lambda: view.objects.author)
        self.assertRaises(KeyError, view.objects.get_author)
        self.assertEqual(user, view.objects.user)
        self.assertEqual(user, view.objects.get_user())
        self.assertRaises(AttributeError, lambda: view.objects.a)
        self.assertRaises(AttributeError, lambda: view.objects.get_a)

        # Test preprocess function
        review = view.objects.get_review(lambda r: r.select_related("poster"))

        with assert_max_queries(n=0):
            review.poster

        with assert_max_queries(n=0):
            view.objects.review.poster

        # Second call should override cache
        view.objects.get_review()
        with list_queries() as l:
            view.objects.review.poster
        self.assertEqual(1, len(l))

        # Consecutive calls should result in same object
        self.assertTrue(view.objects.review is view.objects.review)

class TestTesting(unittest.TestCase):
    def do_n_queries(self, _n=1, contextmanager=None, *args, **kwargs):
        with contextmanager(*args, **kwargs) as l:
            for i in range(_n):
                list(Paper.objects.only("id").filter(id=i))
        return l

    def _test_list_queries(self):
        query = [
            'SELECT "main_paper"."id" FROM "main_paper" WHERE "main_paper"."id" = 0',
            'QUERY = \'SELECT "main_paper"."id" FROM "main_paper" WHERE "main_paper"."id" = %s \' - PARAMS = (0,)'
        ]

        settings.DEBUG = False
        queries = self.do_n_queries(_n=1, contextmanager=list_queries, destination=[])
        self.assertEqual(1, len(queries))
        self.assertTrue(queries[0]['sql'].strip() in query)
        self.assertFalse(settings.DEBUG)

        settings.DEBUG = True
        queries = self.do_n_queries(_n=1, contextmanager=list_queries, destination=[])
        self.assertEqual(1, len(queries))
        self.assertTrue(queries[0]['sql'].strip() in query)
        self.assertTrue(settings.DEBUG)

        queries = self.do_n_queries(_n=1, contextmanager=list_queries)
        self.assertIsNotNone(queries)

    def test_list_queries(self):
        prev_debug = settings.DEBUG

        try:
            self._test_list_queries()
        finally:
            settings.DEBUG = prev_debug

    def test_assert_max_queries(self):
        self.assertRaises(AssertionError, self.do_n_queries, 1, assert_max_queries, 0)
        self.assertRaises(AssertionError, self.do_n_queries, 5, assert_max_queries, 4)
        self.assertRaises(AssertionError, self.do_n_queries, 10, assert_max_queries, 9)
        self.do_n_queries(1, assert_max_queries, 1)
        self.do_n_queries(10, assert_max_queries, 15)
