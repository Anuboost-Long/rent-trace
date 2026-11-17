from accounts.tests.base import AuthApiTestCase


class ResendVerificationTests(AuthApiTestCase):
    def test_resend_verification_is_rate_limited_per_email(self):
        self.sign_up()
        first = self.post("/api/auth/resend-verification/", {"email": "ann@example.com"})
        second = self.post("/api/auth/resend-verification/", {"email": "ann@example.com"})
        self.assertEqual((first.status_code, second.status_code), (202, 429))
