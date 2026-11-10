from django.db import transaction
from django.utils import timezone

from properties.models import PropertyFileKind
from properties.services.shared.property_files import (
    find_property_file,
    live_property_files,
    mark_deleted,
)


@transaction.atomic
def delete_property_file(*, actor, property_id, property_file_id, owned_by=None, unit_id=None):
    target = find_property_file(property_id, property_file_id, owned_by, unit_id, for_update=True)
    was_cover = target.is_cover
    mark_deleted(target, actor, timezone.now())
    if not was_cover:
        return
    next_photo = (
        live_property_files(property_id, unit_id=unit_id)
        .filter(kind=PropertyFileKind.PHOTO)
        .order_by("sort_order", "id")
        .first()
    )
    if next_photo is not None:
        next_photo.is_cover = True
        next_photo.updated_by = actor
        next_photo.row_version += 1
        next_photo.save()
