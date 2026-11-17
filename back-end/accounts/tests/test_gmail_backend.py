import base64
from unittest import mock

from django.core.mail import EmailMessage
from django.test import SimpleTestCase, override_settings
from requests import HTTPError, Response

from accounts.integrations.gmail_backend import SEND_URL, GmailApiBackend


def _response(status_code):
    response = Response()
    response.status_code = status_code
    return response


@override_settings(
    GMAIL_CLIENT_ID="id", GMAIL_CLIENT_SECRET="secret", GMAIL_REFRESH_TOKEN="refresh"
)
@mock.patch("accounts.integrations.gmail_backend.AuthorizedSession")
class GmailApiBackendTests(SimpleTestCase):
    message = EmailMessage("Hello", "Body text", "RentTrace <a@example.com>", ["b@example.com"])

    def test_posts_the_encoded_message_to_gmail(self, session_class):
        session_class.return_value.post.return_value = _response(200)

        sent = GmailApiBackend().send_messages([self.message])

        self.assertEqual(sent, 1)
        url = session_class.return_value.post.call_args.args[0]
        raw = session_class.return_value.post.call_args.kwargs["json"]["raw"]
        self.assertEqual(url, SEND_URL)
        self.assertIn(b"Subject: Hello", base64.urlsafe_b64decode(raw))

    def test_uses_the_refresh_token_from_settings(self, session_class):
        session_class.return_value.post.return_value = _response(200)

        GmailApiBackend().send_messages([self.message])

        credentials = session_class.call_args.args[0]
        self.assertEqual(credentials.refresh_token, "refresh")
        self.assertEqual(credentials.client_id, "id")

    def test_failure_raises(self, session_class):
        session_class.return_value.post.return_value = _response(403)

        with self.assertRaises(HTTPError):
            GmailApiBackend().send_messages([self.message])

    def test_failure_is_swallowed_when_fail_silently(self, session_class):
        session_class.return_value.post.return_value = _response(403)

        sent = GmailApiBackend(fail_silently=True).send_messages([self.message])

        self.assertEqual(sent, 0)
