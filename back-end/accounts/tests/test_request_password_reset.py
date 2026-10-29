from django.core import mail

from accounts.tests.base import AuthApiTestCase


class RequestPasswordResetTests(AuthApiTestCase):
    def test_forgot_password_does_not_reveal_accounts(self):
        self.verified_user()
        mail.outbox.clear()
        known = self.post("/api/auth/forgot-password/", {"email": "ann@example.com"})
        unknown = self.post("/api/auth/forgot-password/", {"email": "nobody@example.com"})
        self.assertEqual((known.status_code, known.data), (unknown.status_code, unknown.data))
        self.assertEqual(len(mail.outbox), 1)
