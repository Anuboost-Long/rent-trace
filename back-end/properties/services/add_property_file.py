import uuid

from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Max
from rest_framework.exceptions import NotFound, ValidationError

from files.models import File, UploadStatus
from properties.models import PropertyFile, PropertyFileKind
from properties.services.shared.property_files import live_property_files
from properties.services.shared.queries import live_properties
from properties.services.shared.units import ensure_unit_in_property
from properties.services.shared.uploads import (
    LIMIT_MESSAGE,
    LIMITS,
    check_upload,
    sha256_of,
)


def add_property_file(
    *, actor, property_id, upload, kind, caption=None, owned_by=None, unit_id=None
):
    if unit_id is not None:
        ensure_unit_in_property(property_id, unit_id, owned_by)
    mime_type, extension = check_upload(upload, kind)
    checksum = sha256_of(upload)
    folder = f"properties/{property_id}" + (f"/units/{unit_id}" if unit_id else "")
    key = default_storage.save(f"{folder}/{uuid.uuid4().hex}.{extension}", upload)
    try:
        return _record(
            actor, property_id, unit_id, upload, kind, caption, owned_by, key, mime_type, checksum
        )
    except Exception:
        default_storage.delete(key)
        raise


@transaction.atomic
def _record(actor, property_id, unit_id, upload, kind, caption, owned_by, key, mime_type, checksum):
    target = live_properties(owned_by).select_for_update().filter(pk=property_id).first()
    if target is None:
        raise NotFound("No property with this id.")
    scope = live_property_files(property_id, unit_id=unit_id)
    existing = scope.filter(kind=kind)
    if existing.count() >= LIMITS[kind]:
        raise ValidationError({"file": LIMIT_MESSAGE[kind]})
    stored = File.objects.create(
        original_name=upload.name[:255],
        object_key=key,
        mime_type=mime_type,
        size_bytes=upload.size,
        sha256=checksum,
        upload_status=UploadStatus.READY,
        uploaded_by=actor,
        created_by=actor,
    )
    next_order = (existing.aggregate(Max("sort_order"))["sort_order__max"] or 0) + 1
    has_cover = scope.filter(is_cover=True).exists()
    return PropertyFile.objects.create(
        property=target,
        property_unit_id=unit_id,
        file=stored,
        kind=kind,
        caption=caption or None,
        is_cover=kind == PropertyFileKind.PHOTO and not has_cover,
        sort_order=next_order,
        created_by=actor,
    )
