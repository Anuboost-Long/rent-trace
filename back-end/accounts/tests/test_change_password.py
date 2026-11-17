from accounts.tests.base import PASSWORD, AuthApiTestCase


class ChangePasswordTests(AuthApiTestCase):
    def test_change_password_keeps_this_session_and_can_sign_out_others(self):
        self.verified_user()
        other = self.sign_in().data
        this = self.sign_in().data
        self.authorize(this["access_token"])

        wrong = self.post(
            "/api/auth/change-password/",
            {"current_password": "not it at all", "new_password": "a fresh strong secret"},
        )
        self.assertEqual(wrong.status_code, 400)

        response = self.post(
            "/api/auth/change-password/",
            {
                "current_password": PASSWORD,
                "new_password": "a fresh strong secret",
                "sign_out_other_devices": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)
        self.authorize(other["access_token"])
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
