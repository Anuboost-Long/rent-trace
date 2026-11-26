import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from accounts.integrations import email_layout
from accounts.models import AuthMethod

logger = logging.getLogger(__name__)


def _send(user, subject, heading, paragraphs, button=None, footnote=""):
    paragraphs = [f"Hi {user.first_name},", *paragraphs]
    text_parts = [*paragraphs, *([f"{button[0]}:\n{button[1]}"] if button else []), footnote]
    try:
        message = EmailMultiAlternatives(
            subject, "\n\n".join(filter(None, text_parts)), None, [user.email]
        )
        message.attach_alternative(
            email_layout.render(heading, paragraphs, button, footnote), "text/html"
        )
        message.send()
    except Exception:
        logger.exception("Auth email '%s' to user %s failed", subject, user.pk)
        return False
    return True


def _link(base_url, path, raw_token):
    return f"{base_url}/{path}?token={raw_token}"


def send_verification(user, raw_token):
    _send(
        user,
        "Verify your RentTrace email",
        "Verify your email",
        ["Confirm your email address to finish signing up."],
        button=("Verify email", _link(settings.WEB_APP_URL, "verify-email", raw_token)),
        footnote="The link expires in 24 hours. If you didn't sign up, ignore this email.",
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
        "You already have an account",
        [
            "Someone tried to sign up with this email, but it already has an account.",
            f"{method}.",
        ],
        footnote="If this wasn't you, you can ignore this email.",
    )


def send_password_reset(user, raw_token):
    _send(
        user,
        "Reset your RentTrace password",
        "Reset your password",
        ["We received a request to reset your password."],
        button=(
            "Choose a new password",
            _link(settings.WEB_APP_URL, "reset-password", raw_token),
        ),
        footnote="The link expires in 1 hour. If you didn't ask for this, ignore this email; "
        "your password stays the same.",
    )


def send_password_changed(user):
    _send(
        user,
        "Your RentTrace password was changed",
        "Your password was changed",
        ["The password for your RentTrace account was just changed."],
        button=("Reset it again", f"{settings.WEB_APP_URL}/auth/forgot-password"),
        footnote="If this was you, there is nothing more to do. If it wasn't, reset your "
        "password now and contact support.",
    )


def send_authenticator_reset(user):
    return _send(
        user,
        "Your RentTrace authenticator was reset",
        "Your authenticator was reset",
        [
            "A super admin reset the two-step verification on your RentTrace account, "
            "and you were signed out everywhere.",
            "The next time you sign in you will be asked to set up a new authenticator app.",
        ],
        footnote="If you did not ask for this, contact support straight away.",
    )


def send_wrong_method(user, attempted_method):
    if attempted_method == AuthMethod.GOOGLE:
        attempt, fix = "with Google", "Sign in with your email and password instead"
    else:
        attempt, fix = "with a password", "Use Sign in with Google instead"
    _send(
        user,
        "Sign-in attempt on your RentTrace account",
        "Sign-in attempt on your account",
        [
            f"Someone tried to sign in to your account {attempt}, "
            "but your account doesn't use that method.",
            f"{fix}.",
        ],
        footnote="If this wasn't you, you can ignore this email.",
    )
