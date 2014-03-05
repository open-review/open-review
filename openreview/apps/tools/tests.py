import unittest
from django.core.urlresolvers import reverse
from django.test import Client
from openreview.apps.tools.testing import disable_pipeline


class TestDisablePipeline(unittest.TestCase):
    """
    Pipeline shows peculiar behaviour when used in test environments. As a result, we disable
    it when using Client with disable_pipeline(). This test checks whether pipeline indeed
    crashes when enabled, and if disabling it helps.

    See: http://stackoverflow.com/questions/12816941/unit-testing-with-django-pipeline
    """
    def fetch(self):
        c = Client()
        c.post(reverse("frontpage"))

    def test_pipeline(self):
        self.assertRaises(ValueError, self.fetch())

    def test_disable_pipeline(self):
        @disable_pipeline
        def pipeline_disabled_fetch():
            self.fetch()

        self.assertEqual(pipeline_disabled_fetch(), None)

