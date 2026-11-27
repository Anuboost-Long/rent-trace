import uuid

from django.core.files.storage import default_storage
from django.db import transaction
from rest_framework.exceptions import ValidationError

from files.models import File, UploadStatus
from properties.models import PropertyFileKind
from properties.services.shared.uploads import check_upload, sha256_of
from reviews.models import ReviewSubmissionFile
from reviews.services.shared.decisions import require_pending
from reviews.services.shared.scope import find_evidence_I_wrote, reloaded

MAX_PHOTOS = 5
TOO_MANY = f"A report can have up to {MAX_PHOTOS} photos."


def add_evidence_photo(*, user, request_id, upload):
    mime_type, extension = check_upload(upload, PropertyFileKind.PHOTO)
    checksum = sha256_of(upload)
    key = default_storage.save(f"evidence/{request_id}/{uuid.uuid4().hex}.{extension}", upload)
    try:
        return _record(user, request_id, upload, key, mime_type, checksum)
    except Exception:
        default_storage.delete(key)
        raise


@transaction.atomic
def _record(user, request_id, upload, key, mime_type, checksum):
    request = find_evidence_I_wrote(user, request_id, lock=True)
    require_pending(request)
    if request.current_submission.files.count() >= MAX_PHOTOS:
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
    ReviewSubmissionFile.objects.create(
        submission=request.current_submission, file=stored, created_by=user
    )
    return reloaded(request)
