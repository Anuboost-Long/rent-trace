from datetime import timedelta

from rest_framework.exceptions import ValidationError

from accounts.models import AuthToken
from accounts.security import tokens

VERIFICATION_LINK_LIFETIME = timedelta(hours=24)
RESET_LINK_LIFETIME = timedelta(hours=1)
INVALID_LINK = "This link is invalid or has expired. Request a new one."


def issue_link(user, purpose, lifetime, now):
    AuthToken.objects.filter(user=user, purpose=purpose).unused(now).update(expires_at=now)
    raw = tokens.new_secret()
    AuthToken.objects.create(
        user=user, purpose=purpose, token_hash=tokens.digest(raw), expires_at=now + lifetime
    )
    return raw


def use_link(raw, purpose, now):
    token = AuthToken.objects.select_for_update().matching(tokens.digest(raw), purpose).first()
    if token is None or token.used_at is not None or token.expires_at <= now:
        raise ValidationError({"token": INVALID_LINK})
    token.used_at = now
    token.save()
    return token.user
