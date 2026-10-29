import json
import uuid
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from rest_framework.exceptions import APIException, AuthenticationFailed

GOOGLE_SIGN_IN_FAILED = "We couldn't sign you in with Google. Try again."


class GoogleSignInUnavailable(APIException):
    status_code = 503
    default_detail = (
        "Google sign-in isn't available right now. Try again later or use your email and password."
    )
    default_code = "google_unavailable"


@dataclass(frozen=True)
class GoogleIdentity:
    subject: uuid.UUID
    email: str
    full_name: str


def fetch_google_identity(supabase_access_token):
    if not settings.SUPABASE_URL or not settings.SUPABASE_PUBLISHABLE_KEY:
        raise GoogleSignInUnavailable()
    request = Request(
        f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/user",
        headers={
            "Authorization": f"Bearer {supabase_access_token}",
            "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            user = json.load(response)
    except HTTPError as error:
        if error.code in (401, 403):
            raise AuthenticationFailed(GOOGLE_SIGN_IN_FAILED) from error
        raise GoogleSignInUnavailable() from error
    except (URLError, TimeoutError, ValueError) as error:
        raise GoogleSignInUnavailable() from error

    metadata = user.get("user_metadata") or {}
    if (
        (user.get("app_metadata") or {}).get("provider") != "google"
        or not user.get("email")
        or not user.get("email_confirmed_at")
    ):
        raise AuthenticationFailed(GOOGLE_SIGN_IN_FAILED)
    return GoogleIdentity(
        subject=uuid.UUID(user["id"]),
        email=user["email"],
        full_name=metadata.get("full_name") or metadata.get("name") or "",
    )
