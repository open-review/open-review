import os, io, sys
import unittest


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

        # Supress stupid printing of error messages
        actualstdout = sys.stdout
        sys.stdout = io.StringIO()
        self.assertRaises(ValueError, get_bool, "illegal")
        sys.stdout = actualstdout

        self.assertEqual(get_bool("non-existent"), None)
        self.assertEqual(get_bool("non-existent", default=False), False)

        # Supress stupid printing of error messages
        sys.stdout = io.StringIO()
        self.assertRaises(ValueError, get_bool, "non-existent", err_empty=True)
        sys.stdout = actualstdout

    def test_get_bool(self):
        # Save and restore environment variables
        environ = os.environ.copy()
        os.environ.clear()

        try:
            self._test_get_bool()
        finally:
            os.environ.update(environ)
