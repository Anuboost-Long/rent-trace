from accounts.models import User
from accounts.tests.base import AuthApiTestCase


class AuthenticationTests(AuthApiTestCase):
    def test_suspended_user_is_locked_out_immediately(self):
        user = self.verified_user()
        self.authorize(self.sign_in().data["access_token"])
        User.objects.filter(pk=user.pk).update(account_status="SUSPENDED")
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)

    def test_protected_routes_need_a_token(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
        self.authorize("not-a-real-token")
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
