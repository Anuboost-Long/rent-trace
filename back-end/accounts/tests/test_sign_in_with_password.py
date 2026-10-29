from datetime import timedelta

from django.core import mail
from django.utils import timezone

from accounts.models import SignInThrottle
from accounts.tests.base import AuthApiTestCase


class SignInWithPasswordTests(AuthApiTestCase):
    def test_sign_in_failures_lock_and_double(self):
        self.verified_user()
        for _ in range(4):
            self.assertEqual(self.sign_in(password="wrong password here").status_code, 401)
        self.assertIsNone(SignInThrottle.objects.get().locked_until)

        self.sign_in(password="wrong password here")
        throttle = SignInThrottle.objects.get()
        self.assertAlmostEqual(
            (throttle.locked_until - throttle.last_failed_at).total_seconds(), 600, delta=1
        )
        self.assertEqual(self.sign_in().status_code, 401, "correct password is refused while locked")
        self.assertEqual(SignInThrottle.objects.get().failed_count, 5, "attempts while locked aren't counted")

        SignInThrottle.objects.update(locked_until=timezone.now() - timedelta(seconds=1))
        self.sign_in(password="wrong password here")
        throttle = SignInThrottle.objects.get()
        self.assertAlmostEqual(
            (throttle.locked_until - throttle.last_failed_at).total_seconds(), 1200, delta=1
        )

        SignInThrottle.objects.update(locked_until=timezone.now() - timedelta(seconds=1))
        self.assertEqual(self.sign_in().status_code, 200)
        throttle = SignInThrottle.objects.get()
        self.assertEqual((throttle.failed_count, throttle.locked_until), (0, None))

    def test_unknown_email_and_wrong_password_look_the_same(self):
        self.verified_user()
        unknown = self.sign_in(email="nobody@example.com")
        wrong = self.sign_in(password="wrong password here")
        self.assertEqual((unknown.status_code, unknown.data), (wrong.status_code, wrong.data))

    def test_password_sign_in_to_google_account_emails_the_owner(self):
        with self.google_response(email="gina@gmail.com"):
            self.google_sign_in()
        mail.outbox.clear()
        response = self.sign_in(email="gina@gmail.com", password="anything at all")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Use Sign in with Google", mail.outbox[-1].body)
