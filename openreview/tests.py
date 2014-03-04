import os
import unittest

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.test import Client, LiveServerTestCase
from django.conf import settings

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

# Determine the WebDriver module. Defaults to Firefox.
try:
    web_driver_module = settings.SELENIUM_WEBDRIVER
except AttributeError:
    from selenium.webdriver.firefox import webdriver as web_driver_module

class SeleniumWebDriver(web_driver_module.WebDriver):
    """Default webdriver, extended with convenience methods."""

    def find_css(self, css_selector):
        """Shortcut to find elements by CSS. Returns either a list or singleton"""
        elems = self.find_elements_by_css_selector(css_selector)
        found = len(elems)
        if found == 1:
            return elems[0]
        elif not elems:
            raise NoSuchElementException(css_selector)
        return elems

    def wait_for_css(self, css_selector, timeout=7):
        """Shortcut for WebDriverWait"""
        try:
            return WebDriverWait(self, timeout).until(lambda driver: driver.find_css(css_selector))
        except TimeoutException:
            self.quit()

class SeleniumTestCase(LiveServerTestCase):
    """TestCase for in-browser testing. Sets up `wd` property, which is an initialised Selenium
    webdriver (defaults to Firefox)."""
    def open(self, url):
        self.wd.get("%s%s" % (self.live_server_url, url))

    def setUp(self):
        self.wd = SeleniumWebDriver()
        super().setUp()

    def tearDown(self):
        self.wd.quit()
        super().tearDown()

disable_pipeline = override_settings(STATICFILES_STORAGE=settings.TEST_STATICFILES_STORAGE)

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

class TestSettings(unittest.TestCase):
    def _test_get_bool(self):
        from openreview.settings import get_bool

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

        try:
            self._test_get_bool()
        finally:
            os.environ.update(environ)
