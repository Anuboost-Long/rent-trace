import uuid
from dataclasses import dataclass
from datetime import timedelta

from accounts.models import AuthSession, RefreshToken, User
from accounts.security import tokens
from accounts.services.shared.account_rules import has_active_role

SESSION_LIFETIME = timedelta(days=90)
REFRESH_TOKEN_LIFETIME = timedelta(days=30)
SESSION_ENDED = "Your session has ended. Sign in again."


@dataclass(frozen=True)
class Device:
    name: str | None
    user_agent: str | None
    ip_address: str | None


@dataclass(frozen=True)
class SignedIn:
    user: User
    access_token: str
    refresh_token: str
    needs_onboarding: bool


def revoke_sessions(user, now, keep=None):
    open_sessions = user.sessions.open(now)
    if keep is not None:
        open_sessions = open_sessions.exclude(pk=keep.pk)
    open_sessions.update(revoked_at=now)


def start_session(user, method, device, now):
    session = AuthSession.objects.create(
        user=user,
        session_id=uuid.uuid4(),
        verified_method=method,
        verified_at=now,
        expires_at=now + SESSION_LIFETIME,
        last_used_at=now,
        device_name=device.name,
        user_agent=device.user_agent,
        ip_address=device.ip_address,
    )
    user.last_login_at = now
    user.save(update_fields=["last_login_at", "updated_at"])
    return issue_session_tokens(session, now)


def issue_session_tokens(session, now):
    raw = tokens.new_secret()
    RefreshToken.objects.create(
        session=session,
        token_hash=tokens.digest(raw),
        expires_at=min(now + REFRESH_TOKEN_LIFETIME, session.expires_at),
    )
    return SignedIn(
        user=session.user,
        access_token=tokens.issue_access_token(session),
        refresh_token=raw,
        needs_onboarding=not has_active_role(session.user),
    )
