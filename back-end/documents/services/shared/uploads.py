import uuid

from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError

from files.models import File, MimeType, UploadStatus
from properties.services.shared.uploads import MAX_FILE_BYTES, sha256_of, sniff_type

ALLOWED = {MimeType.PDF, MimeType.JPEG, MimeType.PNG}
WRONG_TYPE = "Documents must be PDF, JPEG or PNG files."


def check_document_upload(upload):
    if upload.size == 0 or upload.size > MAX_FILE_BYTES:
        raise ValidationError({"file": "Files must be between 1 byte and 10 MB."})
    mime_type, extension = sniff_type(upload)
    if mime_type not in ALLOWED:
        raise ValidationError({"file": WRONG_TYPE})
    return mime_type, extension


def save_upload(upload, folder, mime_type, extension):
    return default_storage.save(f"{folder}/{uuid.uuid4().hex}.{extension}", upload)


def record_file(user, upload, key, mime_type):
    return File.objects.create(
        original_name=upload.name[:255],
        object_key=key,
        mime_type=mime_type,
        size_bytes=upload.size,
        sha256=sha256_of(upload),
        upload_status=UploadStatus.READY,
        uploaded_by=user,
        created_by=user,
    )
