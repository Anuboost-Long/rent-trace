from django.db import models
from django.db.models import F, Q

from common.models import (
    EventRecord,
    LinkRecord,
    MutableRecord,
    PartySide,
    enum_check,
)

from .targets import ReviewTarget


class ReviewStatus(models.TextChoices):
    DRAFT = "DRAFT"
    WAITING_REVIEWER = "WAITING_REVIEWER"
    PENDING_REVIEW = "PENDING_REVIEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    NEEDS_INFORMATION = "NEEDS_INFORMATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DISPUTED = "DISPUTED"
    CANCELLED = "CANCELLED"
    STALE = "STALE"


class ReviewKind(models.TextChoices):
    EVIDENCE_REVIEW = "EVIDENCE_REVIEW"
    SHARED_CHANGE = "SHARED_CHANGE"
    LOCKED_CORRECTION = "LOCKED_CORRECTION"
    CONTRACT_CHANGE = "CONTRACT_CHANGE"
    DISPUTE = "DISPUTE"
    SETTLEMENT = "SETTLEMENT"
    MAINTENANCE_CLOSURE = "MAINTENANCE_CLOSURE"
    DOCUMENT_CONFIRMATION = "DOCUMENT_CONFIRMATION"
    DATA_REMOVAL = "DATA_REMOVAL"


class ReviewRoute(models.TextChoices):
    OPPOSITE_SIDE = "OPPOSITE_SIDE"
    ADMIN = "ADMIN"
    OWNER_DIRECT = "OWNER_DIRECT"


class ReviewRequest(MutableRecord):
    target = models.ForeignKey(ReviewTarget, models.PROTECT, related_name="requests")
    kind = models.TextField(choices=ReviewKind)
    requested_by = models.ForeignKey(
        "accounts.User", models.PROTECT, related_name="review_requests"
    )
    requester_side = models.TextField(choices=PartySide)
    review_route = models.TextField(choices=ReviewRoute)
    status = models.TextField(choices=ReviewStatus, default=ReviewStatus.DRAFT)
    parent_request = models.ForeignKey(
        "self", models.PROTECT, null=True, blank=True, related_name="child_requests"
    )
    current_submission = models.ForeignKey(
        "ReviewSubmission", models.PROTECT, null=True, blank=True, related_name="+"
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "review_requests"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("review_requests", "kind", ReviewKind),
            enum_check("review_requests", "requester_side", PartySide),
            enum_check("review_requests", "review_route", ReviewRoute),
            enum_check("review_requests", "status", ReviewStatus),
        ]
        indexes = [
            models.Index(
                fields=["status", "review_route", "submitted_at"],
                name="ix_review_requests_queue",
            ),
            models.Index(fields=["target", "status"], name="ix_review_requests_target"),
        ]


class ReviewRequestScope(EventRecord):
    request = models.ForeignKey(ReviewRequest, models.PROTECT, related_name="scopes")
    tenancy = models.ForeignKey("tenancies.Tenancy", models.PROTECT, related_name="review_scopes")
    scope_revision = models.PositiveIntegerField()

    class Meta:
        db_table = "review_request_scopes"
        constraints = [
            models.CheckConstraint(
                condition=Q(scope_revision__gte=1),
                name="ck_review_request_scopes_revision",
            ),
            models.UniqueConstraint(
                fields=["request", "scope_revision", "tenancy"],
                name="uq_review_request_scopes",
            ),
        ]


class ReviewSubmission(EventRecord):
    request = models.ForeignKey(ReviewRequest, models.PROTECT, related_name="submissions")
    revision_no = models.PositiveIntegerField()
    submitted_by = models.ForeignKey(
        "accounts.User", models.PROTECT, related_name="review_submissions"
    )
    expected_row_version = models.BigIntegerField(null=True, blank=True)
    base_condition_version = models.ForeignKey(
        "conditions.ConditionVersion", models.PROTECT, null=True, blank=True, related_name="+"
    )
    proposed_condition_version = models.ForeignKey(
        "conditions.ConditionVersion", models.PROTECT, null=True, blank=True, related_name="+"
    )
    base_document_version = models.ForeignKey(
        "documents.DocumentVersion", models.PROTECT, null=True, blank=True, related_name="+"
    )
    proposed_document_version = models.ForeignKey(
        "documents.DocumentVersion", models.PROTECT, null=True, blank=True, related_name="+"
    )
    before_values = models.JSONField(default=dict)
    proposed_values = models.JSONField(default=dict)
    reason = models.TextField(null=True, blank=True)
    what_is_incorrect = models.TextField(null=True, blank=True)
    proposed_replacement = models.TextField(null=True, blank=True)
    why_change_needed = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "review_submissions"
        constraints = [
            models.CheckConstraint(
                condition=Q(revision_no__gte=1), name="ck_review_submissions_revision"
            ),
            models.UniqueConstraint(
                fields=["request", "revision_no"], name="uq_review_submissions_revision"
            ),
        ]


class ReviewSubmissionFile(LinkRecord):
    submission = models.ForeignKey(ReviewSubmission, models.PROTECT, related_name="files")
    file = models.ForeignKey("files.File", models.PROTECT, related_name="submission_attachments")

    class Meta:
        db_table = "review_submission_files"
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "file"], name="uq_review_submission_files"
            ),
        ]


class ReviewerSide(models.TextChoices):
    LANDLORD = "LANDLORD"
    TENANT = "TENANT"
    ADMIN = "ADMIN"


class ReviewDecisionType(models.TextChoices):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    DISPUTE = "DISPUTE"
    REQUEST_INFORMATION = "REQUEST_INFORMATION"


class ReviewDecision(EventRecord):
    request = models.ForeignKey(ReviewRequest, models.PROTECT, related_name="decisions")
    submission = models.ForeignKey(ReviewSubmission, models.PROTECT, related_name="decisions")
    reviewer = models.ForeignKey("accounts.User", models.PROTECT, related_name="review_decisions")
    reviewer_side = models.TextField(choices=ReviewerSide)
    decision = models.TextField(choices=ReviewDecisionType)
    reason = models.TextField(null=True, blank=True)
    idempotency_key = models.UUIDField(unique=True)

    class Meta:
        db_table = "review_decisions"
        constraints = [
            enum_check("review_decisions", "reviewer_side", ReviewerSide),
            enum_check("review_decisions", "decision", ReviewDecisionType),
            models.CheckConstraint(
                condition=Q(decision="APPROVE") & ~Q(reviewer_side="ADMIN")
                | Q(reason__isnull=False),
                name="ck_review_decisions_reason",
            ),
            models.UniqueConstraint(
                fields=["request"],
                condition=Q(decision__in=["APPROVE", "REJECT", "DISPUTE"]),
                name="uq_terminal_review_decision",
            ),
        ]


class ReviewStatusHistory(EventRecord):
    request = models.ForeignKey(ReviewRequest, models.PROTECT, related_name="status_history")
    sequence_no = models.PositiveBigIntegerField()
    from_status = models.CharField(max_length=30, null=True, blank=True)
    to_status = models.CharField(max_length=30, choices=ReviewStatus)
    action = models.CharField(max_length=60)
    actor = models.ForeignKey(
        "accounts.User", models.PROTECT, null=True, blank=True, related_name="review_status_events"
    )
    on_behalf_of = models.ForeignKey(
        "accounts.User", models.PROTECT, null=True, blank=True, related_name="+"
    )
    submission = models.ForeignKey(
        ReviewSubmission, models.PROTECT, null=True, blank=True, related_name="status_events"
    )
    decision = models.ForeignKey(
        ReviewDecision, models.PROTECT, null=True, blank=True, related_name="status_events"
    )
    reason = models.TextField()
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "review_status_history"
        constraints = [
            enum_check("review_status_history", "from_status", ReviewStatus),
            enum_check("review_status_history", "to_status", ReviewStatus),
            models.UniqueConstraint(
                fields=["request", "sequence_no"], name="uq_review_status_history_seq"
            ),
            models.CheckConstraint(
                condition=Q(on_behalf_of__isnull=True) | ~Q(on_behalf_of=F("actor")),
                name="ck_review_status_history_on_behalf_of",
            ),
        ]
