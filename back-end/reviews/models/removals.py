from django.db import models

from common.models import EventRecord, enum_check

from .requests import ReviewRequest
from .targets import ReviewTarget


class RemovalRequestItem(EventRecord):
    request = models.ForeignKey(
        ReviewRequest, models.PROTECT, related_name="removal_items"
    )
    target = models.ForeignKey(
        ReviewTarget, models.PROTECT, related_name="removal_items"
    )
    include_descendants = models.BooleanField(default=True)
    requested_reason = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "removal_request_items"
        constraints = [
            models.UniqueConstraint(
                fields=["request", "target"], name="uq_removal_request_items"
            ),
        ]


class RemovalEffectType(models.TextChoices):
    HIDE_RECORD = "HIDE_RECORD"
    HIDE_DESCENDANTS = "HIDE_DESCENDANTS"
    HIDE_FILE = "HIDE_FILE"


class RemovalEffect(EventRecord):
    request = models.ForeignKey(
        ReviewRequest, models.PROTECT, related_name="removal_effects"
    )
    target = models.ForeignKey(
        ReviewTarget, models.PROTECT, related_name="removal_effects"
    )
    effect = models.TextField(choices=RemovalEffectType)
    reason = models.TextField()

    class Meta:
        db_table = "removal_effects"
        constraints = [
            enum_check("removal_effects", "effect", RemovalEffectType),
            models.UniqueConstraint(
                fields=["request", "target", "effect"], name="uq_removal_effects"
            ),
        ]
