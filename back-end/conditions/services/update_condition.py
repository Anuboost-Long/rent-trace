from django.db import transaction

from conditions.services.shared.scope import find_owned_note
from conditions.services.shared.versions import add_version

WORDING = ("title", "description", "observed_at")


@transaction.atomic
def update_condition(*, landlord, condition_id, changes):
    note = find_owned_note(landlord, condition_id, lock=True)
    current = note.accepted_version
    if any(field in changes for field in WORDING):
        add_version(
            note,
            landlord,
            title=changes.get("title", current.title),
            description=(
                (changes["description"] or None)
                if "description" in changes
                else current.condition_description
            ),
            observed_at=changes.get("observed_at", current.observed_at),
        )
    if "is_shown_to_tenants" in changes:
        note.is_shown_to_tenants = changes["is_shown_to_tenants"]
    note.updated_by = landlord
    note.row_version += 1
    note.save()
    return note
