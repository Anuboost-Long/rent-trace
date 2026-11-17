from django.db import models
from django.db.models import Prefetch, Q

from common.models import LinkRecord, MutableRecord, enum_check, nonblank_check
from properties.models import PropertyOwner


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
        null=True,
        blank=True,
        related_name="communication_logs",
    )
    tenancy = models.ForeignKey(
        "tenancies.Tenancy",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="communication_logs",
    )
    maintenance_issue = models.ForeignKey(
        "maintenance.MaintenanceIssue",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="communication_logs",
    )
    service_provider = models.ForeignKey(
        "providers.ServiceProvider",
        models.PROTECT,
        null=True,
        blank=True,
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
    communication_log = models.ForeignKey(CommunicationLog, models.PROTECT, related_name="files")
    file = models.ForeignKey("files.File", models.PROTECT, related_name="communication_attachments")

    class Meta:
        db_table = "communication_log_files"
        constraints = [
            models.UniqueConstraint(
                fields=["communication_log", "file"], name="uq_communication_log_files"
            ),
        ]


class ContactRequestStatus(models.TextChoices):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    CANCELLED = "CANCELLED"
    REVOKED = "REVOKED"


OPEN_STATUSES = [ContactRequestStatus.PENDING, ContactRequestStatus.ACCEPTED]


class ContactRequestQuerySet(models.QuerySet):
    def live(self):
        return self.filter(deleted_at__isnull=True)

    def open(self):
        return self.live().filter(status__in=OPEN_STATUSES)

    def with_status(self, status):
        return self.filter(status=status)

    def matching(self, text):
        return self.filter(
            Q(property__property_name__icontains=text)
            | Q(property__suburb__icontains=text)
            | Q(tenant__first_name__icontains=text)
            | Q(tenant__last_name__icontains=text)
        )

    def with_details(self):
        primary_owners = PropertyOwner.objects.filter(
            is_primary_owner=True, valid_to__isnull=True, deleted_at__isnull=True
        ).select_related("owner")
        return self.select_related("property", "property_unit", "tenant").prefetch_related(
            Prefetch("property__owners", queryset=primary_owners, to_attr="primary_owners")
        )


class ContactRequest(MutableRecord):
    property = models.ForeignKey(
        "properties.Property", models.PROTECT, related_name="contact_requests"
    )
    property_unit = models.ForeignKey(
        "properties.PropertyUnit",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="contact_requests",
    )
    tenant = models.ForeignKey("accounts.User", models.PROTECT, related_name="contact_requests")
    message = models.TextField()
    status = models.TextField(choices=ContactRequestStatus, default=ContactRequestStatus.PENDING)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        "accounts.User", models.PROTECT, null=True, blank=True, related_name="+"
    )

    objects = ContactRequestQuerySet.as_manager()

    class Meta(MutableRecord.Meta):
        db_table = "contact_requests"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("contact_requests", "status", ContactRequestStatus),
            nonblank_check("contact_requests", "message"),
            models.CheckConstraint(
                condition=Q(status=ContactRequestStatus.PENDING, decided_at__isnull=True)
                | (~Q(status=ContactRequestStatus.PENDING) & Q(decided_at__isnull=False)),
                name="ck_contact_requests_decided",
            ),
            models.UniqueConstraint(
                fields=["tenant", "property"],
                condition=Q(status__in=OPEN_STATUSES, deleted_at__isnull=True),
                name="uq_contact_requests_open",
            ),
        ]
        indexes = [
            models.Index(fields=["property", "status"], name="ix_contact_requests_property"),
            models.Index(fields=["tenant", "status"], name="ix_contact_requests_tenant"),
        ]
