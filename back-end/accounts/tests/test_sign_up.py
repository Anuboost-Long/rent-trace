from datetime import timedelta

from django.core import mail
from django.utils import timezone

from accounts.models import Ban, User, UserCredential
from accounts.tests.base import AuthApiTestCase


class SignUpTests(AuthApiTestCase):
    def test_sign_up_verify_sign_in_and_me(self):
        response = self.sign_up(email=" Ann@Example.com ")
        self.assertEqual(response.status_code, 202)
        user = User.objects.get()
        self.assertEqual(user.email_normalized, "ann@example.com")
        self.assertIsNone(user.email_verified_at)
        self.assertTrue(UserCredential.objects.filter(user=user).exists())

        self.assertEqual(self.sign_in().status_code, 403)

        self.post("/api/auth/verify-email/", {"token": self.last_link_token()})
        response = self.sign_in()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["needs_onboarding"])
        self.assertEqual(response.data["user"]["roles"], ["TENANT"])

        self.authorize(response.data["access_token"])
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["email"], "Ann@Example.com")

    def test_weak_password_is_rejected(self):
        for weak in ["short", "1234567890123", "password123", "annexample.com"]:
            response = self.sign_up(password=weak)
            self.assertEqual(response.status_code, 400, weak)
        self.assertFalse(User.objects.exists())

    def test_sign_up_with_registered_email_gives_same_reply(self):
        self.verified_user()
        mail.outbox.clear()
        response = self.sign_up(password="another strong secret")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(User.objects.count(), 1)
        self.assertIn("already has an account", mail.outbox[-1].body)

    def test_unverified_account_is_reclaimed_after_seven_days(self):
        self.sign_up()
        User.objects.update(created_at=timezone.now() - timedelta(days=8))
        self.sign_up(password="brand new strong secret", first_name="Real", role="LANDLORD")
        user = User.objects.get()
        self.assertEqual(user.first_name, "Real")
        self.post("/api/auth/verify-email/", {"token": self.last_link_token()})
        response = self.sign_in(password="brand new strong secret")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["roles"], ["LANDLORD"])
        self.assertTrue(user.access_history.filter(action="RECLAIM_UNVERIFIED").exists())

    def test_banned_email_cannot_sign_up(self):
        Ban.objects.create(ban_type="EMAIL_DOMAIN", value="spam.test", reason="Fraud reports")
        response = self.sign_up(email="bot@spam.test")
        self.assertEqual(response.status_code, 202)
        self.assertFalse(User.objects.exists())
        self.assertEqual(len(mail.outbox), 0)
