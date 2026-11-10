from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.integrations.gmail_backend import SEND_SCOPE, TOKEN_URI


class Command(BaseCommand):
    help = (
        "Sign in as the sending Gmail account in your browser and print the refresh token "
        "for GMAIL_REFRESH_TOKEN. Needs GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET in config/.env."
    )

    def handle(self, **_):
        from google_auth_oauthlib.flow import InstalledAppFlow

        if not (settings.GMAIL_CLIENT_ID and settings.GMAIL_CLIENT_SECRET):
            raise CommandError("Set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET in config/.env first.")

        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": TOKEN_URI,
                }
            },
            scopes=[SEND_SCOPE],
        )
        credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        self.stdout.write(f"GMAIL_REFRESH_TOKEN={credentials.refresh_token}")
