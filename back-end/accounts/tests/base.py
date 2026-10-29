import json
import re
import uuid
from unittest import mock

from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase

from accounts.models import User

PASSWORD = "correct horse battery"
LOCAL_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@override_settings(
    CACHES=LOCAL_CACHE,
    SUPABASE_URL="https://example.supabase.co",
    SUPABASE_PUBLISHABLE_KEY="test-key",
)
class AuthApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()

    def post(self, path, data=None, **kwargs):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(path, data, format="json", **kwargs)

    def sign_up(self, email="ann@example.com", password=PASSWORD, role="TENANT", **extra):
        payload = {
            "email": email,
            "password": password,
            "first_name": "Ann",
            "last_name": "Lee",
            "role": role,
        }
        return self.post("/api/auth/sign-up/", {**payload, **extra})

    def last_link_token(self):
        return re.search(r"token=([\w-]+)", mail.outbox[-1].body).group(1)

    def verified_user(self, email="ann@example.com"):
        self.sign_up(email=email)
        self.post("/api/auth/verify-email/", {"token": self.last_link_token()})
        return User.objects.get(email_normalized=email)

    def sign_in(self, email="ann@example.com", password=PASSWORD):
        return self.post("/api/auth/sign-in/", {"email": email, "password": password})

    def authorize(self, access_token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def google_response(self, email="gina@gmail.com", subject=None, provider="google"):
        body = {
            "id": str(subject or uuid.uuid4()),
            "email": email,
            "email_confirmed_at": "2026-10-29T00:00:00Z",
            "app_metadata": {"provider": provider},
            "user_metadata": {"full_name": "Gina Mary Park"},
        }
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = json.dumps(body).encode()
        return mock.patch("accounts.integrations.supabase.urlopen", return_value=response)

    def google_sign_in(self):
        return self.post("/api/auth/google/", {"access_token": "supabase-token"})
