from accounts.models import AuthSession
from accounts.tests.base import AuthApiTestCase


class ResetPasswordTests(AuthApiTestCase):
    def test_reset_password_signs_out_other_devices_by_default(self):
        self.verified_user()
        self.sign_in()
        self.post("/api/auth/forgot-password/", {"email": "ann@example.com"})
        response = self.post(
            "/api/auth/reset-password/",
            {"token": self.last_link_token(), "new_password": "a fresh strong secret"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(AuthSession.objects.get().revoked_at)
        self.assertEqual(self.sign_in().status_code, 401)
        self.assertEqual(self.sign_in(password="a fresh strong secret").status_code, 200)
