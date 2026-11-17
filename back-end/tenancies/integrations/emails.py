import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from accounts.integrations import email_layout

logger = logging.getLogger(__name__)


def _send(subject, heading, to, paragraphs, button, footnote):
    link_text, link = button
    try:
        message = EmailMultiAlternatives(
            subject,
            "\n\n".join([*paragraphs, f"{link_text}:\n{link}", footnote]),
            None,
            [to],
        )
        message.attach_alternative(
            email_layout.render(heading, paragraphs, button, footnote), "text/html"
        )
        message.send()
    except Exception:
        logger.exception("Tenancy email failed")


def send_invitation(email, sender, place_name, raw_token, needs_landlord_approval=False):
    link = f"{settings.WEB_APP_URL}/invitations/accept?token={raw_token}"
    paragraphs = [
        "Hi,",
        f"{sender.first_name} {sender.last_name} invited you to join a tenancy at {place_name} "
        "on RentTrace.",
    ]
    if needs_landlord_approval:
        paragraphs.append(
            "The landlord also has to approve before you can join. You will be told when they do."
        )
    footnote = (
        "The link expires in 7 days. Sign in or sign up with this email address to accept. "
        "If you weren't expecting this, ignore this email."
    )
    _send(
        "You're invited to a tenancy on RentTrace",
        "You're invited",
        email,
        paragraphs,
        ("View the invitation", link),
        footnote,
    )


def send_housemate_request(owner, requester, place_name):
    link = f"{settings.WEB_APP_URL}/landlord/tenancies"
    paragraphs = [
        f"Hi {owner.first_name},",
        f"{requester.first_name} {requester.last_name}, a tenant at {place_name}, asked to add "
        "someone to their tenancy. Review the request and approve or decline it.",
    ]
    _send(
        "A tenant asked to add a housemate",
        "Review a housemate request",
        owner.email,
        paragraphs,
        ("Review the request", link),
        "The person only joins if you and they both agree.",
    )
