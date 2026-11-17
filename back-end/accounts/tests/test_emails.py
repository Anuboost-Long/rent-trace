from django.core import mail
from django.test import override_settings

from accounts.tests.base import AuthApiTestCase


class AuthEmailTests(AuthApiTestCase):
    @override_settings(WEB_APP_URL="https://app.renttrace.test")
    def test_verification_email_has_a_clickable_button_and_a_plain_text_fallback(self):
        self.sign_up()

        message = mail.outbox[-1]
        html, mime_type = message.alternatives[0]
        token = self.last_link_token()
        self.assertEqual(mime_type, "text/html")
        self.assertIn(f'href="https://app.renttrace.test/verify-email?token={token}"', html)
        self.assertIn("Verify email", html)
        self.assertIn(f"verify-email?token={token}", message.body)

    def test_user_text_is_escaped_in_html(self):
        self.sign_up(first_name="<b>Ann</b>")

        html = mail.outbox[-1].alternatives[0][0]
        self.assertNotIn("<b>Ann</b>", html)
        self.assertIn("&lt;b&gt;Ann&lt;/b&gt;", html)
