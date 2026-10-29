from django.db import models
from django.db.models import Q

from common.models import EventRecord, LinkRecord, MutableRecord, enum_check


class DocumentType(models.TextChoices):
    TENANCY_AGREEMENT = "TENANCY_AGREEMENT"
    CONDITION_REPORT = "CONDITION_REPORT"
    NOTICE = "NOTICE"
    RECEIPT = "RECEIPT"
    OTHER = "OTHER"


class Document(MutableRecord):
    property_unit = models.ForeignKey(
        "properties.PropertyUnit", models.PROTECT, related_name="documents"
    )
    tenancy = models.ForeignKey(
        "tenancies.Tenancy", models.PROTECT, null=True, blank=True, related_name="documents"
    )
    document_type = models.TextField(choices=DocumentType)
    current_version = models.ForeignKey(
        "DocumentVersion", models.PROTECT, null=True, blank=True, related_name="+"
    )

    class Meta(MutableRecord.Meta):
        db_table = "documents"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("documents", "document_type", DocumentType),
        ]


class DocumentVersion(EventRecord):
    document = models.ForeignKey(Document, models.PROTECT, related_name="versions")
    version_no = models.PositiveIntegerField()
    supersedes_version = models.ForeignKey(
        "self", models.PROTECT, null=True, blank=True, related_name="superseded_by"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    document_date = models.DateField(null=True, blank=True)
    uploaded_by = models.ForeignKey(
        "accounts.User", models.PROTECT, related_name="document_versions"
    )
    confirmation_request = models.OneToOneField(
        "reviews.ReviewRequest",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="confirmed_document_version",
    )

    class Meta:
        db_table = "document_versions"
        constraints = [
            models.CheckConstraint(
                condition=Q(version_no__gte=1), name="ck_document_versions_version_no"
            ),
            models.UniqueConstraint(
                fields=["document", "version_no"], name="uq_document_versions_version_no"
            ),
        ]


class DocumentFile(LinkRecord):
    document_version = models.ForeignKey(DocumentVersion, models.PROTECT, related_name="files")
    file = models.ForeignKey("files.File", models.PROTECT, related_name="document_attachments")

    class Meta:
        db_table = "document_files"
        constraints = [
            models.UniqueConstraint(fields=["document_version", "file"], name="uq_document_files"),
        ]
