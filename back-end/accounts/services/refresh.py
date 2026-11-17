from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import RefreshToken
from accounts.security import tokens
from accounts.services.shared.account_rules import is_account_usable
from accounts.services.shared.sessions import SESSION_ENDED, SignedIn, issue_session_tokens


def refresh(raw_refresh_token):
    signed_in = _attempt(raw_refresh_token, timezone.now())
    if signed_in is None:
        raise AuthenticationFailed(SESSION_ENDED)
    return signed_in


@transaction.atomic
def _attempt(raw_refresh_token, now) -> SignedIn | None:
    token_hash = tokens.digest(raw_refresh_token)
    token = RefreshToken.objects.select_for_update().matching(token_hash).first()
    if token is None or not _is_open(token.session, now):
        return None

    session = token.session
    reused_or_blocked = token.used_at is not None or not is_account_usable(session.user, now)
    if reused_or_blocked:
        session.revoked_at = now
        session.save()
        return None
    if token.expires_at <= now:
        return None

    token.used_at = now
    token.save()
    session.last_used_at = now
    session.save()
    return issue_session_tokens(session, now)


def _is_open(session, now):
    return session.revoked_at is None and session.expires_at > now
