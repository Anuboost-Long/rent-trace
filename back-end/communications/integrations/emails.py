import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from accounts.integrations import email_layout

logger = logging.getLogger(__name__)


def _send(user, subject, heading, paragraphs, footnote):
    paragraphs = [f"Hi {user.first_name},", *paragraphs]
    button = ("Open RentTrace", settings.WEB_APP_URL)
    try:
        message = EmailMultiAlternatives(
            subject,
            "\n\n".join([*paragraphs, f"{button[0]}:\n{button[1]}", footnote]),
            None,
            [user.email],
        )
        message.attach_alternative(
            email_layout.render(heading, paragraphs, button, footnote), "text/html"
        )
        message.send()
    except Exception:
        logger.exception("Contact request email '%s' to user %s failed", subject, user.pk)


def send_request_received(landlord, tenant, place_name):
    _send(
        landlord,
        "Someone wants to get in touch about your property",
        "New contact request",
        [
            f"{tenant.first_name} {tenant.last_name} asked to get in touch about {place_name}.",
            "Sign in to read their message and accept or decline.",
        ],
        "Your contact details are only shared if you accept.",
    )


def send_request_answered(tenant, place_name, accepted):
    outcome = "accepted" if accepted else "declined"
    _send(
        tenant,
        f"Your contact request was {outcome}",
        f"Request {outcome}",
        [
            f"Your request to get in touch about {place_name} was {outcome}.",
            "Sign in to see the landlord's details."
            if accepted
            else "You can keep browsing other places.",
        ],
        "RentTrace never shares contact details without the landlord's say-so.",
    )
