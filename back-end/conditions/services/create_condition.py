from django.db import transaction

from conditions.models import ConditionRecord, ConditionRecordType
from conditions.services.shared.scope import find_owned_unit
from conditions.services.shared.versions import add_version


@transaction.atomic
def create_condition(*, landlord, fields):
    unit = find_owned_unit(landlord, fields["unit_id"])
    note = ConditionRecord.objects.create(
        property_unit=unit,
        record_type=ConditionRecordType.BASELINE,
        is_shown_to_tenants=fields.get("is_shown_to_tenants", False),
        created_by=landlord,
        updated_by=landlord,
    )
    add_version(
        note,
        landlord,
        title=fields["title"],
        description=fields.get("description") or None,
        observed_at=fields["observed_at"],
    )
    note.save()
    return note
