from django.db import transaction
from django.utils import timezone

from history.recording import record_business_change
from properties.services.shared.errors import HasTenancies
from properties.services.shared.property_files import live_property_files, mark_deleted
from properties.services.shared.units import find_unit_for_update


@transaction.atomic
def delete_unit(*, actor, property_id, unit_id, owned_by=None):
    unit = find_unit_for_update(property_id, unit_id, owned_by)
    if unit.tenancies.filter(deleted_at__isnull=True).exists():
        raise HasTenancies("This unit has tenancies, so it can't be removed.")
    now = timezone.now()
    for attached in live_property_files(property_id, unit_id=unit.pk):
        mark_deleted(attached, actor, now)
    unit.deleted_at = now
    unit.deleted_by = actor
    unit.updated_by = actor
    unit.row_version += 1
    unit.save()
    record_business_change(
        unit, actor, "DELETE_UNIT", {"deleted": False}, {"deleted": True}, "Removed through the app"
    )
