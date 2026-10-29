from django.db import models
from django.db.models import F, Q

from common.models import (
    EventRecord,
    LinkRecord,
    MutableRecord,
    PartySide,
    enum_check,
)


class MaintenancePriority(models.TextChoices):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class MaintenanceStatus(models.TextChoices):
    REPORTED = "REPORTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class ClosureOutcome(models.TextChoices):
    FIXED = "FIXED"
    NOT_FIXED_NO_ACTION = "NOT_FIXED_NO_ACTION"


class MaintenanceTrigger(models.TextChoices):
    REPORT = "REPORT"
    OPPOSITE_OPEN = "OPPOSITE_OPEN"
    CONFIRM_START = "CONFIRM_START"
    APPROVED_CLOSURE = "APPROVED_CLOSURE"
    VACANT_OWNER_CLOSURE = "VACANT_OWNER_CLOSURE"


class MaintenanceIssue(MutableRecord):
    property_unit = models.ForeignKey(
        "properties.PropertyUnit", models.PROTECT, related_name="maintenance_issues"
    )
    unit_area = models.ForeignKey(
        "properties.UnitArea",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="maintenance_issues",
    )
    tenancy = models.ForeignKey(
        "tenancies.Tenancy",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="maintenance_issues",
    )
    service_category = models.ForeignKey(
        "providers.ServiceCategory",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="maintenance_issues",
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.TextField(choices=MaintenancePriority)
    status = models.TextField(choices=MaintenanceStatus, default=MaintenanceStatus.REPORTED)
    reported_by = models.ForeignKey("accounts.User", models.PROTECT, related_name="reported_issues")
    reporter_side = models.TextField(choices=PartySide)
    reported_at = models.DateTimeField()
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    work_started_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closure_outcome = models.TextField(choices=ClosureOutcome, null=True, blank=True)
    recurrence_of_issue = models.ForeignKey(
        "self", models.PROTECT, null=True, blank=True, related_name="recurrences"
    )

    class Meta(MutableRecord.Meta):
        db_table = "maintenance_issues"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("maintenance_issues", "priority", MaintenancePriority),
            enum_check("maintenance_issues", "status", MaintenanceStatus),
            enum_check("maintenance_issues", "reporter_side", PartySide),
            enum_check("maintenance_issues", "closure_outcome", ClosureOutcome),
            models.CheckConstraint(
                condition=Q(
                    status=MaintenanceStatus.CLOSED,
                    closed_at__isnull=False,
                    closure_outcome__isnull=False,
                )
                | Q(closed_at__isnull=True, closure_outcome__isnull=True)
                & ~Q(status=MaintenanceStatus.CLOSED),
                name="ck_maintenance_issues_closure",
            ),
        ]
        indexes = [
            models.Index(
                fields=["property_unit", "status", "reported_at"],
                name="ix_maintenance_issues_unit",
            ),
        ]


class MaintenanceIssueFile(LinkRecord):
    maintenance_issue = models.ForeignKey(MaintenanceIssue, models.PROTECT, related_name="files")
    file = models.ForeignKey(
        "files.File", models.PROTECT, related_name="maintenance_issue_attachments"
    )
    caption = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "maintenance_issue_files"
        constraints = [
            models.UniqueConstraint(
                fields=["maintenance_issue", "file"], name="uq_maintenance_issue_files"
            ),
        ]


class MaintenanceIssueRead(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    maintenance_issue = models.ForeignKey(MaintenanceIssue, models.PROTECT, related_name="reads")
    user = models.ForeignKey(
        "accounts.User", models.PROTECT, related_name="maintenance_issue_reads"
    )
    first_opened_at = models.DateTimeField()
    notification = models.ForeignKey(
        "notifications.Notification",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="maintenance_issue_reads",
    )

    class Meta:
        db_table = "maintenance_issue_reads"
        constraints = [
            models.UniqueConstraint(
                fields=["maintenance_issue", "user"], name="uq_maintenance_issue_reads"
            ),
        ]


class MaintenanceClosureProposal(EventRecord):
    maintenance_issue = models.ForeignKey(
        MaintenanceIssue, models.PROTECT, related_name="closure_proposals"
    )
    review_request = models.OneToOneField(
        "reviews.ReviewRequest", models.PROTECT, related_name="closure_proposal"
    )
    outcome = models.TextField(choices=ClosureOutcome)
    reason = models.TextField()
    proposed_by = models.ForeignKey(
        "accounts.User", models.PROTECT, related_name="closure_proposals"
    )
    issue_row_version = models.BigIntegerField()

    class Meta:
        db_table = "maintenance_closure_proposals"
        constraints = [
            enum_check("maintenance_closure_proposals", "outcome", ClosureOutcome),
            models.CheckConstraint(
                condition=~Q(reason=""), name="ck_maintenance_closure_proposals_reason"
            ),
        ]


class MaintenanceStatusHistory(EventRecord):
    maintenance_issue = models.ForeignKey(
        MaintenanceIssue, models.PROTECT, related_name="status_history"
    )
    sequence_no = models.PositiveBigIntegerField()
    from_status = models.CharField(max_length=30, null=True, blank=True)
    to_status = models.CharField(max_length=30, choices=MaintenanceStatus)
    trigger = models.TextField(choices=MaintenanceTrigger)
    actor = models.ForeignKey(
        "accounts.User", models.PROTECT, related_name="maintenance_status_events"
    )
    on_behalf_of = models.ForeignKey(
        "accounts.User", models.PROTECT, null=True, blank=True, related_name="+"
    )
    closure_proposal = models.ForeignKey(
        MaintenanceClosureProposal,
        models.PROTECT,
        null=True,
        blank=True,
        related_name="status_events",
    )
    reason = models.TextField()

    class Meta:
        db_table = "maintenance_status_history"
        constraints = [
            enum_check("maintenance_status_history", "from_status", MaintenanceStatus),
            enum_check("maintenance_status_history", "to_status", MaintenanceStatus),
            enum_check("maintenance_status_history", "trigger", MaintenanceTrigger),
            models.UniqueConstraint(
                fields=["maintenance_issue", "sequence_no"],
                name="uq_maintenance_status_history_seq",
            ),
            models.CheckConstraint(
                condition=Q(on_behalf_of__isnull=True) | ~Q(on_behalf_of=F("actor")),
                name="ck_maintenance_status_history_on_behalf_of",
            ),
        ]


class MaintenanceStatusHistoryFile(LinkRecord):
    maintenance_status_history = models.ForeignKey(
        MaintenanceStatusHistory, models.PROTECT, related_name="files"
    )
    file = models.ForeignKey(
        "files.File", models.PROTECT, related_name="maintenance_status_attachments"
    )
    caption = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "maintenance_status_history_files"
        constraints = [
            models.UniqueConstraint(
                fields=["maintenance_status_history", "file"],
                name="uq_maintenance_status_history_files",
            ),
        ]
