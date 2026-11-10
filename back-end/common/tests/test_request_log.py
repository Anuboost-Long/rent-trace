from django.test import SimpleTestCase, override_settings

from accounts.tests.base import AuthApiTestCase


class RequestLogTests(AuthApiTestCase):
    def test_successful_request_is_logged_at_info_with_a_request_id(self):
        with self.assertLogs("renttrace.requests", "INFO") as logs:
            response = self.client.get("/api/auth/signing-key/")

        self.assertEqual(response.status_code, 200)
        line = logs.records[0].getMessage()
        self.assertIn("GET /api/auth/signing-key/ 200", line)
        self.assertIn(f"req={response['X-Request-ID']}", line)

    def test_failed_request_is_logged_at_warning_with_the_field_names_only(self):
        with self.assertLogs("renttrace.requests", "WARNING") as logs:
            self.post("/api/auth/sign-in/", {"email": "not-an-email", "password": "SECRET-VALUE"})

        record = logs.records[0]
        self.assertEqual(record.levelname, "WARNING")
        self.assertIn("400", record.getMessage())
        self.assertIn("fields=['email']", record.getMessage())
        self.assertNotIn("SECRET-VALUE", record.getMessage())

    def test_signed_in_user_id_is_logged_and_query_string_is_not(self):
        user = self.verified_user()
        self.authorize(self.sign_in().data["access_token"])

        with self.assertLogs("renttrace.requests", "INFO") as logs:
            self.client.get("/api/auth/me/?token=abc123")

        line = logs.records[0].getMessage()
        self.assertIn(f"user={user.pk}", line)
        self.assertNotIn("abc123", line)


class UnhandledErrorLogTests(SimpleTestCase):
    @override_settings(ROOT_URLCONF="common.tests.crashing_urls")
    def test_unhandled_exception_is_logged_at_error(self):
        self.client.raise_request_exception = False

        with self.assertLogs("renttrace.requests", "ERROR") as logs:
            response = self.client.get("/crash/")

        self.assertEqual(response.status_code, 500)
        self.assertIn("GET /crash/ 500", logs.records[0].getMessage())
