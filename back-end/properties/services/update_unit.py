from django.db import transaction

from properties.services.shared.fields import blank_to_none, save_changes
from properties.services.shared.rent import check_rent
from properties.services.shared.units import find_unit_for_update


@transaction.atomic
def update_unit(*, actor, property_id, unit_id, changes, owned_by=None):
    unit = find_unit_for_update(property_id, unit_id, owned_by)
    clean = blank_to_none(changes)
    check_rent(
        clean.get("rent_amount", unit.rent_amount),
        clean.get("rent_frequency", unit.rent_frequency),
    )
    save_changes(actor, unit, changes)
    return unit
