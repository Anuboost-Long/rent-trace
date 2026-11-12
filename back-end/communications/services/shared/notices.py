from communications.models import ContactRequestStatus as Status
from communications.services.shared.presentation import listing_title
from notifications.models import NotificationKind as Kind
from notifications.services.shared import notify
from properties.services.shared.queries import current_owner_users

ANSWERS = {
    Status.ACCEPTED: (
        Kind.CONTACT_REQUEST_ACCEPTED,
        "Contact request accepted",
        "{name} accepted your request about {place}. Open it to see their contact details.",
    ),
    Status.DECLINED: (
        Kind.CONTACT_REQUEST_DECLINED,
        "Contact request declined",
        "{name} declined your request about {place}.",
    ),
    Status.REVOKED: (
        Kind.CONTACT_REQUEST_REVOKED,
        "Contact details withdrawn",
        "{name} withdrew their contact details for {place}.",
    ),
}


def _name(person):
    return f"{person.first_name} {person.last_name}"


def request_received(contact_request):
    notify(
        current_owner_users(contact_request.property),
        kind=Kind.CONTACT_REQUEST_RECEIVED,
        title="New contact request",
        body=f"{_name(contact_request.tenant)} asked about {listing_title(contact_request)}.",
        subject_id=contact_request.pk,
    )


def request_cancelled(contact_request):
    notify(
        current_owner_users(contact_request.property),
        kind=Kind.CONTACT_REQUEST_CANCELLED,
        title="Contact request cancelled",
        body=(
            f"{_name(contact_request.tenant)} cancelled their request about "
            f"{listing_title(contact_request)}."
        ),
        subject_id=contact_request.pk,
    )


def request_answered(contact_request, landlord):
    kind, title, body = ANSWERS[contact_request.status]
    notify(
        [contact_request.tenant],
        kind=kind,
        title=title,
        body=body.format(name=_name(landlord), place=listing_title(contact_request)),
        subject_id=contact_request.pk,
    )
