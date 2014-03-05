import unittest
from django.core.urlresolvers import reverse
from django.test.client import Client
from openreview.apps.accounts.forms import is_email, RegisterForm
from openreview.apps.accounts.models import User
from openreview.tests import disable_pipeline, SeleniumTestCase


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
        User.objects.all().delete()
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
        User.objects.all().delete()
        self.assertEqual(set(User.objects.all()), set())
        User.objects.create_user("user", password="password")

        c = Client()
        response = c.post(reverse("accounts-login"), {"username": "user", "password": "fout", "existing": ""})
        self.assertFalse("sessionid" in response.cookies)

        response = c.post(reverse("accounts-login"), {"username": "user", "password": "password", "existing": ""})
        self.assertTrue("sessionid" in response.cookies)


    @disable_pipeline
    def test_redirect(self):
        User.objects.create_user("test", password="password")

        c = Client()
        response = c.post(reverse("accounts-login") + "?next=/blaat", {"username": "test", "password": "password", "existing": ""})
        self.assertTrue(response.url.endswith("/blaat"))
        self.assertEqual(response.status_code, 302)

        c = Client()
        response = c.post(reverse("accounts-login"), {"username": "test", "password": "password", "existing": ""})
        self.assertTrue(response.url.endswith(reverse("frontpage")))
        self.assertEqual(response.status_code, 302)


class TestLoginViewSelenium(SeleniumTestCase):
    def test_login(self):
        User.objects.all().delete()
        self.assertEqual(set(User.objects.all()), set())
        User.objects.create_user("user", password="password")

        # Test correct login
        self.open(reverse('accounts-login'))
        self.assertEqual(self.wd.get_cookie("sessionid"), None)
        self.assertTrue(self.wd.current_url.endswith(reverse("accounts-login")))
        self.wd.find_css("#id_login_username").send_keys("user")
        self.wd.find_css("#id_login_password").send_keys("password")
        self.wd.find_css('input[value="Login"]').click()
        self.assertFalse(self.wd.current_url.endswith(reverse("accounts-login")))
        sessionid1 = self.wd.get_cookie("sessionid")["value"]

        ## Test logout
        self.open(reverse('accounts-logout'))
        sessionid2 = self.wd.get_cookie("sessionid")["value"]
        self.assertNotEqual(sessionid1, sessionid2)

        # Test incorrect login
        self.open(reverse('accounts-login'))
        self.assertTrue(self.wd.current_url.endswith(reverse("accounts-login")))
        self.wd.find_css("#id_login_username").send_keys("user")
        self.wd.find_css("#id_login_password").send_keys("wrong")
        self.wd.find_css('#login').click()
        self.assertTrue(self.wd.current_url.endswith(reverse("accounts-login")))
        self.assertEqual(sessionid2, self.wd.get_cookie("sessionid")["value"])

    def test_register(self):
        User.objects.all().delete()
        self.assertEqual(set(User.objects.all()), set())

        self.open(reverse('accounts-register'))
        self.wd.find_css("#id_register_username").send_keys("abc")
        self.wd.find_css("#id_register_password1").send_keys("abcd")
        self.wd.find_css("#id_register_password2").send_keys("abcd")
        self.wd.find_css('#register').click()
        self.wd.wait_for_css("body")

        self.assertEqual(User.objects.all().count(), 1)
        user = User.objects.all()[0]
        self.assertTrue(user.check_password("abcd"))
        self.assertEqual(user.username, "abc")

