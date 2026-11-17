import base64

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

TOKEN_URI = "https://oauth2.googleapis.com/token"
SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
REQUEST_TIMEOUT_SECONDS = 10


class GmailApiBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        session = AuthorizedSession(
            Credentials(
                token=None,
                refresh_token=settings.GMAIL_REFRESH_TOKEN,
                token_uri=TOKEN_URI,
                client_id=settings.GMAIL_CLIENT_ID,
                client_secret=settings.GMAIL_CLIENT_SECRET,
                scopes=[SEND_SCOPE],
            )
        )
        sent = 0
        for message in email_messages:
            raw = base64.urlsafe_b64encode(message.message().as_bytes()).decode()
            response = session.post(SEND_URL, json={"raw": raw}, timeout=REQUEST_TIMEOUT_SECONDS)
            if response.ok:
                sent += 1
            elif not self.fail_silently:
                response.raise_for_status()
        return sent
