import hashlib

from rest_framework.exceptions import ValidationError

from files.models import MimeType
from properties.models import PropertyFileKind

MAX_FILE_BYTES = 10_000_000
MAX_PHOTOS = 30
MAX_DOCUMENTS = 20
SIGNATURE_BYTES = 8

SIGNATURES = [
    (b"\xff\xd8\xff", MimeType.JPEG, "jpg"),
    (b"\x89PNG\r\n\x1a\n", MimeType.PNG, "png"),
    (b"%PDF-", MimeType.PDF, "pdf"),
]
ALLOWED = {
    PropertyFileKind.PHOTO: {MimeType.JPEG, MimeType.PNG},
    PropertyFileKind.DOCUMENT: {MimeType.PDF},
}
WRONG_TYPE = {
    PropertyFileKind.PHOTO: "Photos must be JPEG or PNG images.",
    PropertyFileKind.DOCUMENT: "Documents must be PDF files.",
}


def sniff_type(upload):
    head = upload.read(SIGNATURE_BYTES)
    upload.seek(0)
    for signature, mime_type, extension in SIGNATURES:
        if head.startswith(signature):
            return mime_type, extension
    return None, None


def check_upload(upload, kind):
    if upload.size == 0 or upload.size > MAX_FILE_BYTES:
        raise ValidationError({"file": "Files must be between 1 byte and 10 MB."})
    mime_type, extension = sniff_type(upload)
    if mime_type not in ALLOWED[kind]:
        raise ValidationError({"file": WRONG_TYPE[kind]})
    return mime_type, extension


def sha256_of(upload):
    digest = hashlib.sha256()
    for chunk in upload.chunks():
        digest.update(chunk)
    upload.seek(0)
    return digest.hexdigest()


LIMITS = {PropertyFileKind.PHOTO: MAX_PHOTOS, PropertyFileKind.DOCUMENT: MAX_DOCUMENTS}
LIMIT_MESSAGE = {
    PropertyFileKind.PHOTO: f"A property can have up to {MAX_PHOTOS} photos.",
    PropertyFileKind.DOCUMENT: f"A property can have up to {MAX_DOCUMENTS} documents.",
}
