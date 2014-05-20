import unittest

from django.core.urlresolvers import reverse
from django.test.client import Client
from openreview.apps.accounts.forms import is_email, RegisterForm, SettingsForm, AccountDeleteForm
from openreview.apps.accounts.models import User
from openreview.apps.tools.testing import BaseTestCase
from openreview.apps.main.models.review import Review
from openreview.apps.tools.testing import SeleniumTestCase, create_test_user, create_test_author, \
    create_test_review, create_test_paper


class TestForms(BaseTestCase):
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


class TestLoginView(BaseTestCase):
    def test_register(self):
        User.objects.all().delete()
        self.assertEqual(set(User.objects.all()), set())

        c = Client()
        response = c.post(reverse("accounts-register"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(User.objects.all()), set())
        self.assertFalse("sessionid" in response.cookies)

        response = c.post(reverse("accounts-register"), {"username": "abc", "password1": "abc2",
                                                         "password2": "abc2", "new": ""})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.all().count(), 1)
        user = User.objects.all()[0]
        self.assertEqual(user.username, "abc")
        self.assertTrue(user.check_password("abc2"))
        self.assertTrue("sessionid" in response.cookies)

    def test_login(self):
        User.objects.all().delete()
        self.assertEqual(set(User.objects.all()), set())
        User.objects.create_user("user", password="password")

        # Login with wrong credentials. We expect no sessionid.
        c = Client()
        response = c.post(reverse("accounts-login"), {"username": "user", "password": "fout", "login": ""})
        self.assertFalse("sessionid" in response.cookies)

        # Login with correct credentials, which we do expect to return a sessionid.
        response = c.post(reverse("accounts-login"), {"username": "user", "password": "password", "login": ""})
        self.assertTrue("sessionid" in response.cookies)

    def test_redirect(self):
        User.objects.create_user("test", password="password")

        c = Client()
        response = c.post(reverse("accounts-login") + "?next=/blaat", {"username": "test", "password": "password",
                                                                       "login": ""})
        self.assertTrue(response.url.endswith("/blaat"))
        self.assertEqual(response.status_code, 302)

        c = Client()
        response = c.post(reverse("accounts-login"), {"username": "test", "password": "password", "login": ""})
        #self.assertTrue(response.url.endswith(reverse("dashboard")))
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
        self.wd.find_css('[name="login"]').click()
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
        self.wd.find_css('[name="login"]').click()
        self.assertTrue(self.wd.current_url.endswith(reverse("accounts-login")))
        self.assertEqual(sessionid2, self.wd.get_cookie("sessionid")["value"])

    def test_register(self):
        User.objects.all().delete()
        self.assertEqual(set(User.objects.all()), set())

        self.open(reverse('accounts-register'))
        self.wd.find_css("#id_register_username").send_keys("abc")
        self.wd.find_css("#id_register_password1").send_keys("abcd")
        self.wd.find_css("#id_register_password2").send_keys("abcd")
        self.wd.find_css('[name=new]').click()
        self.wd.wait_for_css("body")

        self.assertEqual(User.objects.all().count(), 1)
        user = User.objects.all()[0]
        self.assertTrue(user.check_password("abcd"))
        self.assertEqual(user.username, "abc")


class TestSettingsForms(BaseTestCase):
    def setUp(self):
        User.objects.all().delete()
        self.assertEqual(set(User.objects.all()), set())
        self.u = User.objects.create_user(username="TestHero", password="test123")
        super().setUp()

    def test_settings_form(self):
        data = {"password1": "test", "password2": "differentpassword"}
        form = SettingsForm(data=data, instance=self.u)
        self.assertFalse(form.is_valid())

        data = {"password1": "test123", "password2": "test123"}
        form = SettingsForm(data=data, instance=self.u)
        self.assertTrue(form.is_valid())

        data = {"password1": "test", "password2": "test", "email": "pietje@pietenpiet.com"}
        form = SettingsForm(data=data, instance=self.u)
        self.assertTrue(form.is_valid())

        data = {"password1": "test", "password2": "test", "email": "pietje@pietenpiet"}
        form = SettingsForm(data=data, instance=self.u)
        self.assertFalse(form.is_valid())

    def test_username(self):
        # Username may not be changed when sending it with post.
        c = Client()
        c.post(reverse("accounts-login"), {"username": "TestHero", "password": "test123", "login": ""})
        c.post(reverse("accounts-settings"), {"username": "hacker", "password1": "abc2", "password2": "abc2"})
        self.assertEqual(self.u.username, "TestHero")

    def test_change_change_password(self):
        c = Client()

        # Make sure we can login using old password
        self.assertTrue(c.login(username="TestHero", password="test123"))

        # Posting only 'password1' and 'password2' should suffice for changing a password
        c.post(reverse("accounts-settings"), {"password1": "test12345", "password2": "test12345"})
        self.assertTrue(User.objects.get(id=self.u.id).check_password("test12345"), msg="Password did not change")

    def test_reviews(self):
        for n in range(5):
            create_test_review(poster=self.u)

        self.assertEqual(len(self.u.reviews.all()), 5)


class TestSettingsFormLive(SeleniumTestCase):
    def setUp(self):
        User.objects.all().delete()
        self.assertEqual(set(User.objects.all()), set())
        self.a = create_test_author(name="tester")
        User.objects.create_user(username="user", password="password")
        super().setUp()

    def test_settings(self):
        self.open(reverse("accounts-login"))
        self.wd.wait_for_css("body")
        self.wd.find_css("#id_login_username").send_keys("user")
        self.wd.find_css("#id_login_password").send_keys("password")
        self.wd.find_css('[name="login"]').click()
        self.wd.wait_for_css("body")

        # Test changing password
        self.open(reverse("accounts-settings"))
        self.wd.wait_for_css("body")
        self.assertFalse(self.wd.current_url.endswith(reverse("accounts-login")))
        self.wd.find_css("#id_password1").send_keys("test1234")
        self.wd.find_css("#id_password2").send_keys("test1234")
        self.wd.find_css('[name="update-settings"]').click()
        self.wd.wait_for_css("body")
        self.open(reverse("accounts-logout"))
        self.wd.wait_for_css("body")

        self.open(reverse("accounts-settings"))
        self.wd.wait_for_css("body")
        self.wd.find_css("#id_login_username").send_keys("user")
        self.wd.find_css("#id_login_password").send_keys("test1234")
        self.wd.find_css('[name="login"]').click()
        self.wd.wait_for_css("body")
        self.assertTrue(self.wd.current_url.endswith(reverse("accounts-settings")))

        # Test changing email
        self.open(reverse("accounts-settings"))
        self.wd.wait_for_css("body")
        self.wd.find_css("#id_email").send_keys("tester@testingheroes.com")
        self.wd.find_css('[name="update-settings"]').click()
        self.wd.wait_for_css("body")
        user = User.objects.all()[0]
        self.assertEqual(user.email, "tester@testingheroes.com")


class TestDeleteAccount(unittest.TestCase):
    def setUp(self):
        User.objects.all().delete()
        self.assertEqual(set(User.objects.all()), set())
        self.u1 = create_test_user()
        self.u2 = create_test_user()
        self.paper = create_test_paper()
        self.review_u1 = create_test_review(paper=self.paper, poster=self.u1)
        self.review_u2 = create_test_review(paper=self.paper, poster=self.u2)
        self.comment_u2 = create_test_review(parent=self.review_u1, poster=self.u2)
        self.comment_u2_u1 = create_test_review(parent=self.comment_u2, poster=self.u1)
        super().setUp()

    def test_delete_form(self):
        form = AccountDeleteForm(user=self.u1, data={"password": "asdqd12", "option": "delete_all"})
        self.assertFalse(form.is_valid())

        form = AccountDeleteForm(user=self.u1, data={"password": "test", "option": "delete_all"})
        self.assertTrue(form.is_valid())

        form = AccountDeleteForm(user=self.u1, data={"password": "test", "option": "keep_reviews"})
        self.assertTrue(form.is_valid())

        form = AccountDeleteForm(user=self.u1, data={"password": "test"})
        self.assertFalse(form.is_valid())

    def test_delete_all(self):
        self.u2.delete(delete_reviews=True)
        self.assertFalse(User.objects.filter(id=self.u2.id).exists())

        self.review_u2 = Review.objects.get(id=self.review_u2.id)
        self.review_u1 = Review.objects.get(id=self.review_u1.id)
        self.comment_u2 = Review.objects.get(id=self.comment_u2.id)
        self.comment_u2_u1 = Review.objects.get(id=self.comment_u2_u1.id)

        self.assertTrue(self.review_u2.is_deleted)
        self.assertTrue(self.comment_u2.is_deleted)

        self.assertFalse(self.review_u1.is_deleted)
        self.assertFalse(self.comment_u2_u1.is_deleted)

    def test_keep_reviews(self):
        self.u2.delete()

        self.assertFalse(User.objects.filter(id=self.u2.id).exists())

        self.review_u2 = Review.objects.get(id=self.review_u2.id)
        self.review_u1 = Review.objects.get(id=self.review_u1.id)
        self.comment_u2 = Review.objects.get(id=self.comment_u2.id)
        self.comment_u2_u1 = Review.objects.get(id=self.comment_u2_u1.id)

        self.assertFalse(self.review_u2.is_deleted)
        self.assertFalse(self.comment_u2.is_deleted)

        self.assertFalse(self.review_u1.is_deleted)
        self.assertFalse(self.comment_u2_u1.is_deleted)


class TestDeleteAccountFormLive(SeleniumTestCase):
    # TODO: Move to offline test?
    def setUp(self):
        self.user = create_test_user()
        self.review = create_test_review(poster=self.user)
        self.login(username=self.user.username)
        self.open(reverse("accounts-delete"))
        self.wd.wait_for_css("body")
        self.assertFalse(self.wd.current_url.endswith(reverse("accounts-login")))

    def test_wrong_password(self):
        self.wd.find_css("#id_password").send_keys("lkjqdwdwqij")
        self.wd.find_css("#delete").click()
        self.wd.wait_for_css("body")

        # Wrong password entered, so should do nothing.
        self.assertTrue(self.wd.current_url.endswith(reverse("accounts-delete")))
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_delete_including_reviews(self):
        """Test option 'delete all reviews' when deleting user"""
        self.wd.find_css("#id_password").send_keys("test")
        self.wd.find_css('input[value="delete_all"]').click()
        self.wd.find_css("#delete").click()
        self.wd.wait_for_css("body")

        self.assertTrue(Review.objects.get(id=self.review.id).is_deleted)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_preserve_reviews(self):
        """Test option 'delete, but let reviews exist' when deleting user"""
        self.wd.find_css("#id_password").send_keys("test")
        self.wd.find_css("#delete").click()
        self.wd.wait_for_css("body")

        self.assertFalse(Review.objects.get(id=self.review.id).is_deleted)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
