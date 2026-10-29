import uuid

from django.core import mail
from django.test import override_settings

from accounts.models import User
from accounts.tests.base import AuthApiTestCase


class SignInWithGoogleTests(AuthApiTestCase):
    def test_google_sign_in_creates_user_then_onboarding(self):
        subject = uuid.uuid4()
        with self.google_response(subject=subject):
            response = self.google_sign_in()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["needs_onboarding"])
        user = User.objects.get()
        self.assertEqual((user.auth_subject, user.first_name, user.last_name), (subject, "Gina", "Mary Park"))
        self.assertIsNotNone(user.email_verified_at)

        self.authorize(response.data["access_token"])
        onboarding = self.post(
            "/api/auth/onboarding/",
            {"first_name": "Gina", "last_name": "Park", "role": "LANDLORD"},
        )
        self.assertEqual(onboarding.data["roles"], ["LANDLORD"])
        self.assertEqual(
            self.post(
                "/api/auth/onboarding/", {"first_name": "G", "last_name": "P", "role": "TENANT"}
            ).status_code,
            400,
        )

        with self.google_response(subject=subject):
            again = self.google_sign_in()
        self.assertFalse(again.data["needs_onboarding"])
        self.assertEqual(User.objects.count(), 1)

    def test_google_email_owned_by_password_account_is_refused(self):
        self.verified_user(email="gina@gmail.com")
        mail.outbox.clear()
        with self.google_response(email="gina@gmail.com"):
            response = self.google_sign_in()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(User.objects.count(), 1)
        self.assertIn("doesn't use that method", mail.outbox[-1].body)

    def test_non_google_supabase_identity_is_refused(self):
        with self.google_response(provider="github"):
            self.assertEqual(self.google_sign_in().status_code, 401)
        self.assertFalse(User.objects.exists())

    @override_settings(SUPABASE_URL="")
    def test_google_sign_in_unconfigured(self):
        self.assertEqual(self.google_sign_in().status_code, 503)
