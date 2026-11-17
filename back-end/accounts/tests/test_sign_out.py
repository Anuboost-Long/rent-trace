from accounts.tests.base import AuthApiTestCase


class SignOutTests(AuthApiTestCase):
    def test_sign_out_ends_the_session(self):
        self.verified_user()
        self.authorize(self.sign_in().data["access_token"])
        self.assertEqual(self.post("/api/auth/sign-out/").status_code, 204)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
