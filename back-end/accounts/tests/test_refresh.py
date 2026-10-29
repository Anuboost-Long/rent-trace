from accounts.models import AuthSession, RefreshToken
from accounts.tests.base import AuthApiTestCase


class RefreshTests(AuthApiTestCase):
    def test_refresh_rotates_and_reuse_revokes_session(self):
        self.verified_user()
        first = self.sign_in().data["refresh_token"]
        second = self.post("/api/auth/refresh/", {"refresh_token": first})
        self.assertEqual(second.status_code, 200)

        reused = self.post("/api/auth/refresh/", {"refresh_token": first})
        self.assertEqual(reused.status_code, 401)
        self.assertIsNotNone(AuthSession.objects.get().revoked_at)

        current = self.post("/api/auth/refresh/", {"refresh_token": second.data["refresh_token"]})
        self.assertEqual(current.status_code, 401)
        self.assertEqual(RefreshToken.objects.filter(used_at__isnull=True).count(), 1)
