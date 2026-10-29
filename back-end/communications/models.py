from django.db import models

from common.models import LinkRecord, MutableRecord, enum_check


class CommunicationChannel(models.TextChoices):
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    SMS = "SMS"
    IN_PERSON = "IN_PERSON"
    OTHER = "OTHER"


class CommunicationLog(MutableRecord):
    property = models.ForeignKey(
        "properties.Property", models.PROTECT, related_name="communication_logs"
    )
    property_unit = models.ForeignKey(
        "properties.PropertyUnit",
        models.PROTECT,
        null=True, blank=True,
        related_name="communication_logs",
    )
    tenancy = models.ForeignKey(
        "tenancies.Tenancy", models.PROTECT, null=True, blank=True, related_name="communication_logs"
    )
    maintenance_issue = models.ForeignKey(
        "maintenance.MaintenanceIssue",
        models.PROTECT,
        null=True, blank=True,
        related_name="communication_logs",
    )
    service_provider = models.ForeignKey(
        "providers.ServiceProvider",
        models.PROTECT,
        null=True, blank=True,
        related_name="communication_logs",
    )
    contact_name = models.CharField(max_length=150, null=True, blank=True)
    channel = models.TextField(choices=CommunicationChannel)
    subject = models.CharField(max_length=200)
    notes = models.TextField()
    communication_at = models.DateTimeField()

    class Meta(MutableRecord.Meta):
        db_table = "communication_logs"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("communication_logs", "channel", CommunicationChannel),
        ]


class CommunicationLogFile(LinkRecord):
    communication_log = models.ForeignKey(
        CommunicationLog, models.PROTECT, related_name="files"
    )
    file = models.ForeignKey(
        "files.File", models.PROTECT, related_name="communication_attachments"
    )

    class Meta:
        db_table = "communication_log_files"
        constraints = [
            models.UniqueConstraint(
                fields=["communication_log", "file"], name="uq_communication_log_files"
            ),
        ]
