from django.db import models
from django.db.models import Q

from common.models import EventRecord, LinkRecord, MutableRecord, enum_check


class ConditionRecordType(models.TextChoices):
    BASELINE = "BASELINE"
    DISCREPANCY = "DISCREPANCY"
    CONDITION_UPDATE = "CONDITION_UPDATE"


class ConditionRecord(MutableRecord):
    property_unit = models.ForeignKey(
        "properties.PropertyUnit", models.PROTECT, related_name="condition_records"
    )
    unit_area = models.ForeignKey(
        "properties.UnitArea",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="condition_records",
    )
    tenancy = models.ForeignKey(
        "tenancies.Tenancy", models.PROTECT, null=True, blank=True, related_name="condition_records"
    )
    record_type = models.TextField(choices=ConditionRecordType)
    related_record = models.ForeignKey(
        "self", models.PROTECT, null=True, blank=True, related_name="related_records"
    )
    maintenance_issue = models.ForeignKey(
        "maintenance.MaintenanceIssue",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="condition_records",
    )
    accepted_version = models.ForeignKey(
        "ConditionVersion", models.PROTECT, null=True, blank=True, related_name="+"
    )

    class Meta(MutableRecord.Meta):
        db_table = "condition_records"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("condition_records", "record_type", ConditionRecordType),
        ]
        indexes = [
            models.Index(fields=["property_unit", "unit_area"], name="ix_condition_records_unit"),
        ]


class SourceType(models.TextChoices):
    LANDLORD = "LANDLORD"
    TENANT = "TENANT"
    JOINT = "JOINT"
    OTHER = "OTHER"


class ConditionVersion(EventRecord):
    condition_record = models.ForeignKey(ConditionRecord, models.PROTECT, related_name="versions")
    version_no = models.PositiveIntegerField()
    supersedes_version = models.ForeignKey(
        "self", models.PROTECT, null=True, blank=True, related_name="superseded_by"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    condition_description = models.TextField(null=True, blank=True)
    source_type = models.TextField(choices=SourceType)
    source_description = models.TextField(null=True, blank=True)
    observed_at = models.DateTimeField()
    submitted_by = models.ForeignKey(
        "accounts.User", models.PROTECT, related_name="condition_versions"
    )
    submitted_at = models.DateTimeField()

    class Meta:
        db_table = "condition_versions"
        constraints = [
            enum_check("condition_versions", "source_type", SourceType),
            models.CheckConstraint(
                condition=Q(version_no__gte=1), name="ck_condition_versions_version_no"
            ),
            models.UniqueConstraint(
                fields=["condition_record", "version_no"],
                name="uq_condition_versions_version_no",
            ),
        ]


class ConditionRecordFile(LinkRecord):
    condition_version = models.ForeignKey(ConditionVersion, models.PROTECT, related_name="files")
    file = models.ForeignKey("files.File", models.PROTECT, related_name="condition_attachments")
    caption = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "condition_record_files"
        constraints = [
            models.UniqueConstraint(
                fields=["condition_version", "file"], name="uq_condition_record_files"
            ),
        ]
