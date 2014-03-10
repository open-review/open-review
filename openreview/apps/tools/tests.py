import unittest

from django.conf import settings
from openreview.apps.main.models import Paper
from openreview.apps.tools.testing import list_queries, assert_max_queries

__all__ = ["TestTesting"]


class TestTesting(unittest.TestCase):
    def do_n_queries(self, _n=1, contextmanager=None, *args, **kwargs):
        with contextmanager(*args, **kwargs) as l:
            for i in range(_n):
                list(Paper.objects.only("id").filter(id=i))
        return l

    def _test_list_queries(self):
        query = 'SELECT "main_paper"."id" FROM "main_paper" WHERE "main_paper"."id" = 0'

        settings.DEBUG = False
        queries = self.do_n_queries(_n=1, contextmanager=list_queries, destination=[])
        self.assertEqual(1, len(queries))
        self.assertEqual(queries[0]['sql'].strip(), query)
        self.assertFalse(settings.DEBUG)

        settings.DEBUG = True
        queries = self.do_n_queries(_n=1, contextmanager=list_queries, destination=[])
        self.assertEqual(1, len(queries))
        self.assertEqual(queries[0]['sql'].strip(), query)
        self.assertTrue(settings.DEBUG)

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
