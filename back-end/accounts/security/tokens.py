import hashlib
import secrets
from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone

ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
ISSUER = "renttrace-api"
MOBILE_AUDIENCE = "renttrace-mobile"
SIGNING_ALGORITHM = "HS256"
SIGNING_KEY_ID = "1"


def new_secret():
    return secrets.token_urlsafe(32)


def digest(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def issue_access_token(session, audience=MOBILE_AUDIENCE):
    now = timezone.now()
    claims = {
        "sub": str(session.user_id),
        "sid": str(session.session_id),
        "iss": ISSUER,
        "aud": audience,
        "iat": now,
        "exp": now + ACCESS_TOKEN_LIFETIME,
    }
    return jwt.encode(
        claims,
        settings.JWT_SIGNING_KEY,
        algorithm=SIGNING_ALGORITHM,
        headers={"kid": SIGNING_KEY_ID},
    )


def decode_access_token(raw, audience=MOBILE_AUDIENCE):
    return jwt.decode(
        raw,
        settings.JWT_SIGNING_KEY,
        algorithms=[SIGNING_ALGORITHM],
        audience=audience,
        issuer=ISSUER,
        options={"require": ["exp", "iat", "sub", "sid"]},
    )
