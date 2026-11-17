from django.test import override_settings

from accounts.tests.base import TEST_API_KEY, AuthApiTestCase

SIGNING_KEY_URL = "/api/auth/signing-key/"


class ApiKeyTests(AuthApiTestCase):
    def test_a_request_without_the_key_is_rejected(self):
        del self.client.defaults["HTTP_X_API_KEY"]

        response = self.client.get(SIGNING_KEY_URL)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"detail": "A valid API key is required.", "code": "invalid_api_key"},
        )

    def test_a_wrong_key_is_rejected(self):
        self.client.defaults["HTTP_X_API_KEY"] = TEST_API_KEY + "x"

        self.assertEqual(self.client.get(SIGNING_KEY_URL).status_code, 401)

    def test_the_right_key_lets_the_request_through(self):
        self.assertEqual(self.client.get(SIGNING_KEY_URL).status_code, 200)

    def test_a_valid_sign_in_token_is_not_enough_without_the_key(self):
        self.verified_user()
        self.authorize(self.sign_in().data["access_token"])
        del self.client.defaults["HTTP_X_API_KEY"]

        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)

    def test_public_sign_in_needs_the_key_too(self):
        del self.client.defaults["HTTP_X_API_KEY"]

        response = self.post("/api/auth/sign-in/", {"email": "a@example.com", "password": "x"})

        self.assertEqual(response.status_code, 401)

    @override_settings(API_KEY="")
    def test_with_no_key_configured_nothing_gets_through(self):
        self.client.defaults["HTTP_X_API_KEY"] = ""

        self.assertEqual(self.client.get(SIGNING_KEY_URL).status_code, 401)

    def test_the_api_docs_pages_stay_open(self):
        del self.client.defaults["HTTP_X_API_KEY"]

        self.assertEqual(self.client.get("/api/docs/").status_code, 200)

    def test_rejected_requests_are_logged_without_the_key(self):
        self.client.defaults["HTTP_X_API_KEY"] = "secret-attempt"

        with self.assertLogs("renttrace.requests", "WARNING") as logs:
            self.client.get(SIGNING_KEY_URL)

        self.assertNotIn("secret-attempt", logs.records[0].getMessage())
        self.assertIn("401", logs.records[0].getMessage())
