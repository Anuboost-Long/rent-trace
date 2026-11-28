import uuid

from django.core.files.storage import default_storage
from django.db import transaction
from rest_framework.exceptions import ValidationError

from files.models import File, UploadStatus
from maintenance.models import MaintenanceIssueFile, MaintenanceStatus
from maintenance.services.shared.scope import find_issue
from properties.models import PropertyFileKind
from properties.services.shared.uploads import check_upload, sha256_of

MAX_PHOTOS = 10
TOO_MANY = f"An issue can have up to {MAX_PHOTOS} photos."
CLOSED = "This issue is closed, so photos can no longer be added."


def add_issue_photo(*, user, issue_id, upload, caption=None):
    mime_type, extension = check_upload(upload, PropertyFileKind.PHOTO)
    checksum = sha256_of(upload)
    key = default_storage.save(f"maintenance/{issue_id}/{uuid.uuid4().hex}.{extension}", upload)
    try:
        return _record(user, issue_id, upload, caption, key, mime_type, checksum)
    except Exception:
        default_storage.delete(key)
        raise


@transaction.atomic
def _record(user, issue_id, upload, caption, key, mime_type, checksum):
    issue = find_issue(user, issue_id, lock=True)
    if issue.status == MaintenanceStatus.CLOSED:
        raise ValidationError({"issue": CLOSED})
    shown = issue.files.filter(file__deleted_at__isnull=True)
    if shown.count() >= MAX_PHOTOS:
        raise ValidationError({"file": TOO_MANY})
    stored = File.objects.create(
        original_name=upload.name[:255],
        object_key=key,
        mime_type=mime_type,
        size_bytes=upload.size,
        sha256=checksum,
        upload_status=UploadStatus.READY,
        uploaded_by=user,
        created_by=user,
    )
    MaintenanceIssueFile.objects.create(
        maintenance_issue=issue, file=stored, caption=caption or None, created_by=user
    )
    return issue.pk
