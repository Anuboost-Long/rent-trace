from django.db import transaction
from django.utils import timezone

from conditions.services.shared.scope import find_owned_note


@transaction.atomic
def delete_condition(*, landlord, condition_id):
    note = find_owned_note(landlord, condition_id, lock=True)
    note.deleted_at = timezone.now()
    note.deleted_by = landlord
    note.updated_by = landlord
    note.row_version += 1
    note.save()
