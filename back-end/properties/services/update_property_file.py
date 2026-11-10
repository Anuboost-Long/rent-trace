from django.db import transaction
from rest_framework.exceptions import ValidationError

from properties.models import PropertyFileKind
from properties.services.shared.fields import save_changes
from properties.services.shared.property_files import find_property_file, live_property_files


@transaction.atomic
def update_property_file(
    *, actor, property_id, property_file_id, changes, owned_by=None, unit_id=None
):
    target = find_property_file(property_id, property_file_id, owned_by, unit_id, for_update=True)
    if changes.get("is_cover") and target.kind != PropertyFileKind.PHOTO:
        raise ValidationError({"is_cover": "Only a photo can be the cover."})
    if changes.get("is_cover"):
        live_property_files(property_id, unit_id=unit_id).filter(is_cover=True).exclude(
            pk=target.pk
        ).update(is_cover=False, updated_by=actor)
    save_changes(actor, target, changes)
    return target
