from rest_framework.exceptions import NotFound

from conditions.models import ConditionRecord, ConditionRecordType
from properties.models import PropertyUnit
from properties.services.shared.queries import live_properties


def find_owned_unit(landlord, unit_id):
    unit = PropertyUnit.objects.filter(
        pk=unit_id, property__in=live_properties(landlord), deleted_at__isnull=True
    ).first()
    if unit is None:
        raise NotFound("No unit with this id.")
    return unit


def unit_notes(unit_id):
    return ConditionRecord.objects.filter(
        property_unit_id=unit_id,
        record_type=ConditionRecordType.BASELINE,
        deleted_at__isnull=True,
    ).select_related("accepted_version")


def find_owned_note(landlord, condition_id, *, lock=False):
    notes = ConditionRecord.objects.filter(
        pk=condition_id,
        record_type=ConditionRecordType.BASELINE,
        property_unit__property__in=live_properties(landlord),
        deleted_at__isnull=True,
    ).select_related("accepted_version")
    if lock:
        notes = notes.select_for_update(of=("self",))
    found = notes.first()
    if found is None:
        raise NotFound("No condition note with this id.")
    return found
