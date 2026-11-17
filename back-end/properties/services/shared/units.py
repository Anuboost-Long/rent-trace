from rest_framework.exceptions import NotFound

from properties.models import PropertyUnit
from properties.services.shared.queries import live_properties


def ensure_unit_in_property(property_id, unit_id, owned_by=None):
    in_property = PropertyUnit.objects.filter(
        pk=unit_id,
        property_id=property_id,
        property__in=live_properties(owned_by),
        deleted_at__isnull=True,
    )
    if not in_property.exists():
        raise NotFound("No unit with this id on this property.")


def find_unit_for_update(property_id, unit_id, owned_by=None):
    unit = (
        PropertyUnit.objects.select_for_update()
        .filter(
            pk=unit_id,
            property_id=property_id,
            property__in=live_properties(owned_by),
            deleted_at__isnull=True,
        )
        .first()
    )
    if unit is None:
        raise NotFound("No unit with this id on this property.")
    return unit
