import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from accounts.integrations import email_layout

logger = logging.getLogger(__name__)


def send_invitation(email, sender, place_name, raw_token):
    link = f"{settings.WEB_APP_URL}/invitations/accept?token={raw_token}"
    paragraphs = [
        "Hi,",
        f"{sender.first_name} {sender.last_name} invited you to join a tenancy at {place_name} "
        "on RentTrace.",
    ]
    footnote = (
        "The link expires in 7 days. Sign in or sign up with this email address to accept. "
        "If you weren't expecting this, ignore this email."
    )
    try:
        message = EmailMultiAlternatives(
            "You're invited to a tenancy on RentTrace",
            "\n\n".join([*paragraphs, f"View the invitation:\n{link}", footnote]),
            None,
            [email],
        )
        message.attach_alternative(
            email_layout.render(
                "You're invited", paragraphs, ("View the invitation", link), footnote
            ),
            "text/html",
        )
        message.send()
    except Exception:
        logger.exception("Tenancy invitation email to invitation recipient failed")
