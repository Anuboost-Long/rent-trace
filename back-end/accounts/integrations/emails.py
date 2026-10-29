import logging

from django.conf import settings
from django.core.mail import send_mail

from accounts.models import AuthMethod

logger = logging.getLogger(__name__)


def _send(user, subject, body):
    try:
        send_mail(subject, body, None, [user.email])
    except Exception:
        logger.exception("Auth email '%s' to user %s failed", subject, user.pk)


def _link(path, raw_token):
    return f"{settings.AUTH_LINK_BASE_URL}/{path}?token={raw_token}"


def send_verification(user, raw_token):
    _send(
        user,
        "Verify your RentTrace email",
        f"Hi {user.first_name},\n\n"
        f"Open this link to verify your email and finish signing up:\n"
        f"{_link('verify-email', raw_token)}\n\n"
        "The link expires in 24 hours. If you didn't sign up, ignore this email.",
    )


def send_already_registered(user):
    method = (
        "Sign in with Google"
        if user.auth_method == AuthMethod.GOOGLE
        else "Sign in with your email and password, or reset your password if you've forgotten it"
    )
    _send(
        user,
        "You already have a RentTrace account",
        f"Hi {user.first_name},\n\n"
        f"Someone tried to sign up with this email, but it already has an account.\n"
        f"{method}.\n\n"
        "If this wasn't you, you can ignore this email.",
    )


def send_password_reset(user, raw_token):
    _send(
        user,
        "Reset your RentTrace password",
        f"Hi {user.first_name},\n\n"
        f"Open this link to choose a new password:\n"
        f"{_link('reset-password', raw_token)}\n\n"
        "The link expires in 1 hour. If you didn't ask for this, ignore this email; "
        "your password stays the same.",
    )


def send_wrong_method(user, attempted_method):
    if attempted_method == AuthMethod.GOOGLE:
        attempt, fix = "with Google", "Sign in with your email and password instead"
    else:
        attempt, fix = "with a password", "Use Sign in with Google instead"
    _send(
        user,
        "Sign-in attempt on your RentTrace account",
        f"Hi {user.first_name},\n\n"
        f"Someone tried to sign in to your account {attempt}, but your account doesn't use that method.\n"
        f"{fix}.\n\n"
        "If this wasn't you, you can ignore this email.",
    )
