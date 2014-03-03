import unittest
from django.core.urlresolvers import reverse
from django.test.client import Client
from openreview.apps.accounts.forms import is_email, RegisterForm
from openreview.apps.accounts.models import User
from openreview.tests import disable_pipeline

class TestForms(unittest.TestCase):
    def test_is_email(self):
        # It is way too hard to test for all valid emails. Assuming correctness in validate_email().
        self.assertTrue(is_email("bla@bla.nl"))
        self.assertFalse(is_email("bla@bla"))

    def test_register_form(self):
        form = RegisterForm(data={"username": "bla@bla.nl", "password1": "test", "password2": "test"})
        self.assertFalse(form.is_valid())

        form = RegisterForm(data={"username": "!!!", "password1": "test", "password2": "test"})
        self.assertFalse(form.is_valid())

        form = RegisterForm(data={"username": "bla@bla", "password1": "test", "password2": "test"})
        self.assertTrue(form.is_valid())

        form = RegisterForm(data={"username": "bla@bla", "password1": "tes", "password2": "test"})
        self.assertFalse(form.is_valid())

    # Assuming UserCreationForm is already tested

class TestLoginView(unittest.TestCase):
    @disable_pipeline
    def test_register(self):
        self.assertEqual(set(User.objects.all()), set())

        c = Client()
        response = c.post(reverse("accounts-register"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(User.objects.all()), set())
        self.assertFalse("sessionid" in response.cookies)

        response = c.post(reverse("accounts-register"), {"username": "abc", "password1": "abc2", "password2": "abc2", "new": ""})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.all().count(), 1)
        user = User.objects.all()[0]
        self.assertEqual(user.username, "abc")
        self.assertTrue(user.check_password("abc2"))
        self.assertTrue("sessionid" in response.cookies)

    @disable_pipeline
    def test_login(self):
        User.objects.create_user("user", password="password")

        c = Client()
        response = c.post(reverse("accounts-login"), {"username": "user", "password": "fout", "existing": ""})
        self.assertFalse("sessionid" in response.cookies)

        response = c.post(reverse("accounts-login"), {"username": "user", "password": "password", "existing": ""})
        self.assertTrue("sessionid" in response.cookies)

