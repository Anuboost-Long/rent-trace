from django.test import override_settings

from accounts.models import AccountAccessHistory, User
from accounts.tests.base import PASSWORD, AuthApiTestCase

SECRET = "setup-secret-for-tests"
URL = "/api/auth/bootstrap-admin/"


@override_settings(ADMIN_BOOTSTRAP_SECRET=SECRET)
class BootstrapAdminTests(AuthApiTestCase):
    def bootstrap(self, **extra):
        payload = {
            "secret": SECRET,
            "email": "root@example.com",
            "password": PASSWORD,
            "first_name": "Root",
            "last_name": "Admin",
        }
        return self.post(URL, {**payload, **extra})

    def test_creates_a_verified_super_admin_who_can_sign_in(self):
        response = self.bootstrap()

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email_normalized="root@example.com")
        self.assertTrue(user.is_top_level_admin)
        self.assertIsNotNone(user.email_verified_at)
        self.assertEqual(AccountAccessHistory.objects.get().action, "BOOTSTRAP_SUPER_ADMIN")
        signed_in = self.sign_in(email="root@example.com")
        self.assertEqual(signed_in.status_code, 200)
        self.assertEqual(signed_in.data["user"]["roles"], ["ADMIN"])

    def test_wrong_secret_is_refused_and_creates_nothing(self):
        response = self.bootstrap(secret="nope")

        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.exists())

    @override_settings(ADMIN_BOOTSTRAP_SECRET="")
    def test_unset_secret_turns_the_endpoint_off(self):
        self.assertEqual(self.bootstrap().status_code, 503)

    def test_only_the_first_call_works(self):
        self.bootstrap()

        second = self.bootstrap(email="other@example.com")

        self.assertEqual(second.status_code, 409)
        self.assertEqual(User.objects.super_admins().count(), 1)

    def test_existing_email_is_refused(self):
        self.verified_user(email="root@example.com")

        response = self.bootstrap()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.super_admins().exists())

    def test_weak_password_is_refused(self):
        response = self.bootstrap(password="short")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.exists())
