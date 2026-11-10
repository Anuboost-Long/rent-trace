from rest_framework.exceptions import NotFound

from properties.models import PropertyFile
from properties.services.shared.queries import live_properties


def live_property_files(property_id, owned_by=None, unit_id=None):
    """Files of one scope: a unit's own files, or the property's own when `unit_id` is None."""
    return PropertyFile.objects.filter(
        property_id=property_id,
        property__in=live_properties(owned_by),
        property_unit_id=unit_id,
        deleted_at__isnull=True,
    ).select_related("file")


def find_property_file(
    property_id, property_file_id, owned_by=None, unit_id=None, *, for_update=False
):
    files = live_property_files(property_id, owned_by, unit_id)
    if for_update:
        files = files.select_for_update(of=("self",))
    found = files.filter(pk=property_file_id).first()
    if found is None:
        raise NotFound("No file with this id here.")
    return found


def mark_deleted(property_file, actor, now):
    for record in (property_file.file, property_file):
        record.deleted_at = now
        record.deleted_by = actor
        record.updated_by = actor
        record.row_version += 1
    property_file.is_cover = False
    property_file.file.save()
    property_file.save()
