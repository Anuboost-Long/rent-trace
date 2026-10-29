from django.db import models
from django.db.models import Q

from common.models import MutableRecord, enum_check


class MimeType(models.TextChoices):
    JPEG = "image/jpeg"
    PNG = "image/png"
    PDF = "application/pdf"


class UploadStatus(models.TextChoices):
    STAGED = "STAGED"
    READY = "READY"
    FAILED = "FAILED"


class File(MutableRecord):
    original_name = models.CharField(max_length=255)
    object_key = models.TextField(unique=True)
    mime_type = models.CharField(max_length=100, choices=MimeType)
    size_bytes = models.BigIntegerField()
    sha256 = models.CharField(max_length=64)
    upload_status = models.TextField(choices=UploadStatus, default=UploadStatus.STAGED)
    uploaded_by = models.ForeignKey("accounts.User", models.PROTECT, related_name="uploaded_files")

    class Meta(MutableRecord.Meta):
        db_table = "files"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("files", "mime_type", MimeType),
            enum_check("files", "upload_status", UploadStatus),
            models.CheckConstraint(
                condition=Q(size_bytes__gt=0, size_bytes__lte=10_000_000),
                name="ck_files_size_bytes",
            ),
        ]
