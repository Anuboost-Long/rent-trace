from django.db import transaction
from rest_framework.exceptions import ValidationError

from accounts.services.shared.mail import send_after_commit
from communications.integrations import emails
from communications.models import ContactRequest, ContactRequestStatus
from communications.services.shared import notices
from communications.services.shared.presentation import listing_title, primary_owner
from listings.services.shared.queries import AVAILABLE_OCCUPANCY, listed_properties
from properties.models import PropertyUnit

MAX_PENDING_PER_TENANT = 10


@transaction.atomic
def create_contact_request(*, tenant, fields):
    listing = listed_properties().filter(pk=fields["listing_id"]).first()
    if listing is None:
        raise ValidationError({"listing_id": "This listing isn't available."})
    unit = _available_unit(listing, fields.get("unit_id"))
    _check_can_ask(tenant, listing)
    created = ContactRequest.objects.create(
        property=listing,
        property_unit=unit,
        tenant=tenant,
        message=fields["message"],
        created_by=tenant,
    )
    loaded = ContactRequest.objects.with_details().get(pk=created.pk)
    notices.request_received(loaded)
    owner = primary_owner(loaded)
    if owner is not None:
        send_after_commit(emails.send_request_received, owner, tenant, listing_title(loaded))
    return loaded


def _available_unit(listing, unit_id):
    if unit_id is None:
        return None
    unit = PropertyUnit.objects.filter(
        pk=unit_id,
        property=listing,
        is_public=True,
        deleted_at__isnull=True,
        occupancy_status__in=AVAILABLE_OCCUPANCY,
    ).first()
    if unit is None:
        raise ValidationError({"unit_id": "This unit isn't available."})
    return unit


def _check_can_ask(tenant, listing):
    mine = ContactRequest.objects.filter(tenant=tenant)
    if mine.open().filter(property=listing).exists():
        raise ValidationError({"listing_id": "You already have a request for this property."})
    pending = mine.live().with_status(ContactRequestStatus.PENDING).count()
    if pending >= MAX_PENDING_PER_TENANT:
        raise ValidationError(
            {"listing_id": "You have too many requests waiting. Cancel one or wait for answers."}
        )
