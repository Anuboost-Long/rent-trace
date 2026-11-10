from django.db import transaction

from properties.services.shared.fields import save_changes
from properties.services.shared.units import find_unit_for_update


@transaction.atomic
def update_unit(*, actor, property_id, unit_id, changes, owned_by=None):
    unit = find_unit_for_update(property_id, unit_id, owned_by)
    save_changes(actor, unit, changes)
    return unit
