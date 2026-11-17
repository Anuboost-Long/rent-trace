from accounts.tests.base import AuthApiTestCase


class VerifyEmailTests(AuthApiTestCase):
    def test_verification_link_works_once(self):
        self.sign_up()
        token = self.last_link_token()
        self.assertEqual(self.post("/api/auth/verify-email/", {"token": token}).status_code, 200)
        self.assertEqual(self.post("/api/auth/verify-email/", {"token": token}).status_code, 400)
