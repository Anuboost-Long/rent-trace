from datetime import timedelta

from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import APIException, AuthenticationFailed, PermissionDenied

from accounts.integrations import emails
from accounts.models import AuthMethod, SignInThrottle, User, UserCredential
from accounts.services.shared.account_rules import is_account_usable, normalize_email
from accounts.services.shared.mail import send_after_commit
from accounts.services.shared.passwords import dummy_password_hash
from accounts.services.shared.sessions import SignedIn, start_session

FREE_SIGN_IN_ATTEMPTS = 5
FIRST_LOCK = timedelta(minutes=10)
MAX_LOCK_DOUBLINGS = 30
SIGN_IN_FAILED = "Email or password is incorrect."
VERIFY_EMAIL_FIRST = "Verify your email before signing in. Check your inbox for the link."


def sign_in_with_password(*, email, password, device):
    outcome = _attempt(normalize_email(email), password, device, timezone.now())
    if isinstance(outcome, APIException):
        raise outcome
    return outcome


@transaction.atomic
def _attempt(email_normalized, password, device, now) -> SignedIn | APIException:
    throttle, _ = SignInThrottle.objects.select_for_update().get_or_create(
        email_normalized=email_normalized
    )
    if _is_locked(throttle, now):
        return AuthenticationFailed(SIGN_IN_FAILED)

    credential = UserCredential.objects.for_email(email_normalized).first()
    password_ok = check_password(
        password, credential.password_hash if credential else dummy_password_hash()
    )
    if credential is None or not password_ok:
        _record_failure(throttle, now)
        return AuthenticationFailed(SIGN_IN_FAILED)

    _clear_failures(throttle)
    user = credential.user
    if user.email_verified_at is None:
        return PermissionDenied(VERIFY_EMAIL_FIRST)
    if not is_account_usable(user, now):
        return AuthenticationFailed(SIGN_IN_FAILED)
    return start_session(user, AuthMethod.EMAIL_PASSWORD, device, now)


def _is_locked(throttle, now):
    return throttle.locked_until is not None and throttle.locked_until > now


def _record_failure(throttle, now):
    throttle.failed_count += 1
    throttle.last_failed_at = now
    if throttle.failed_count >= FREE_SIGN_IN_ATTEMPTS:
        throttle.locked_until = now + lock_duration(throttle.failed_count)
    throttle.save()
    google_user = (
        User.objects.with_email(throttle.email_normalized).google_accounts().not_deleted().first()
    )
    if google_user is not None:
        send_after_commit(emails.send_wrong_method, google_user, AuthMethod.EMAIL_PASSWORD)


def _clear_failures(throttle):
    throttle.failed_count, throttle.last_failed_at, throttle.locked_until = 0, None, None
    throttle.save()


def lock_duration(failed_count):
    doublings = min(failed_count - FREE_SIGN_IN_ATTEMPTS, MAX_LOCK_DOUBLINGS)
    return FIRST_LOCK * 2**doublings
