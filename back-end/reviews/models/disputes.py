from django.db import models

from common.models import EventRecord, enum_check

from .requests import ReviewRequest, ReviewSubmission


class Dispute(EventRecord):
    request = models.OneToOneField(
        ReviewRequest, models.PROTECT, related_name="dispute"
    )
    origin_request = models.ForeignKey(
        ReviewRequest, models.PROTECT, related_name="originated_disputes"
    )
    opened_by = models.ForeignKey(
        "accounts.User", models.PROTECT, related_name="opened_disputes"
    )
    disputed_submission = models.ForeignKey(
        ReviewSubmission, models.PROTECT, related_name="disputes"
    )
    details = models.TextField()

    class Meta:
        db_table = "disputes"


class DisputeOutcome(models.TextChoices):
    SETTLED = "SETTLED"
    ADMIN_APPROVED = "ADMIN_APPROVED"
    ADMIN_REJECTED = "ADMIN_REJECTED"


class DisputeResolution(EventRecord):
    dispute = models.OneToOneField(Dispute, models.PROTECT, related_name="resolution")
    resolution_request = models.ForeignKey(
        ReviewRequest, models.PROTECT, related_name="dispute_resolutions"
    )
    outcome = models.TextField(choices=DisputeOutcome)
    result_condition_version = models.ForeignKey(
        "conditions.ConditionVersion", models.PROTECT, null=True, blank=True, related_name="+"
    )
    result_document_version = models.ForeignKey(
        "documents.DocumentVersion", models.PROTECT, null=True, blank=True, related_name="+"
    )
    reason = models.TextField()

    class Meta:
        db_table = "dispute_resolutions"
        constraints = [
            enum_check("dispute_resolutions", "outcome", DisputeOutcome),
        ]
