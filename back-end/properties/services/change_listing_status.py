from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from properties.models import ListingStatus, PropertyStatus
from properties.services.get_property import get_property
from properties.services.shared.fields import save_changes
from properties.services.shared.queries import live_properties

PUBLIC = {ListingStatus.AVAILABLE, ListingStatus.PARTIALLY_AVAILABLE}
ADMIN_ONLY = {ListingStatus.SUSPENDED, ListingStatus.ARCHIVED}


@transaction.atomic
def change_listing_status(*, actor, property_id, listing_status, owned_by=None, as_admin=False):
    target = live_properties(owned_by).select_for_update().filter(pk=property_id).first()
    if target is None:
        raise NotFound("No property with this id.")
    if not as_admin:
        _check_landlord_may_change(target, listing_status)
    if listing_status in PUBLIC:
        _check_can_be_listed(target)
    save_changes(actor, target, {"listing_status": listing_status}, action="CHANGE_LISTING_STATUS")
    return get_property(property_id=property_id, owned_by=owned_by)


def _check_landlord_may_change(target, listing_status):
    if target.listing_status in ADMIN_ONLY:
        raise PermissionDenied("An admin has locked this listing. Contact support to change it.")
    if listing_status in ADMIN_ONLY:
        raise ValidationError({"listing_status": "Only an admin can set this status."})


def _check_can_be_listed(target):
    if target.property_status != PropertyStatus.ACTIVE:
        raise ValidationError({"listing_status": "Only active properties can be listed."})
    if not target.units.filter(is_public=True, deleted_at__isnull=True).exists():
        raise ValidationError(
            {"listing_status": "Make at least one unit public before listing the property."}
        )
