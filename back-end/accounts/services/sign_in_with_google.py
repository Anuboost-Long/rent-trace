from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed

from accounts.integrations import emails
from accounts.integrations.supabase import GOOGLE_SIGN_IN_FAILED, fetch_google_identity
from accounts.models import AuthMethod, User
from accounts.services.shared.account_rules import (
    is_account_usable,
    is_identity_banned,
    normalize_email,
)
from accounts.services.shared.mail import send_after_commit
from accounts.services.shared.sessions import SignedIn, start_session


def sign_in_with_google(*, supabase_access_token, device):
    identity = fetch_google_identity(supabase_access_token)
    signed_in = _attempt(identity, device, timezone.now())
    if signed_in is None:
        raise AuthenticationFailed(GOOGLE_SIGN_IN_FAILED)
    return signed_in


@transaction.atomic
def _attempt(identity, device, now) -> SignedIn | None:
    user = User.objects.select_for_update().with_subject(identity.subject).first()
    if user is None:
        user = _create_user(identity, now)
    if user is None or not is_account_usable(user, now):
        return None
    return start_session(user, AuthMethod.GOOGLE, device, now)


def _create_user(identity, now):
    email_normalized = normalize_email(identity.email)
    existing = User.objects.with_email(email_normalized).first()
    if existing is not None and existing.auth_method == AuthMethod.EMAIL_PASSWORD:
        send_after_commit(emails.send_wrong_method, existing, AuthMethod.GOOGLE)
    if existing is not None or is_identity_banned(email_normalized, now):
        return None

    fallback = email_normalized.split("@", 1)[0]
    first, _, last = identity.full_name.strip().partition(" ")
    return User.objects.create(
        auth_subject=identity.subject,
        email=identity.email,
        email_normalized=email_normalized,
        email_verified_at=now,
        auth_method=AuthMethod.GOOGLE,
        first_name=first or fallback,
        last_name=last.strip() or fallback,
    )
