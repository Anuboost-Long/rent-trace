from django.db import models
from django.db.models import F, Q

from common.models import EventRecord


class BusinessChangeHistory(EventRecord):
    target = models.ForeignKey(
        "reviews.ReviewTarget", models.PROTECT, related_name="change_history"
    )
    sequence_no = models.PositiveBigIntegerField()
    request = models.ForeignKey(
        "reviews.ReviewRequest",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="change_history",
    )
    action = models.CharField(max_length=60)
    on_behalf_of = models.ForeignKey(
        "accounts.User", models.PROTECT, null=True, blank=True, related_name="+"
    )
    before_values = models.JSONField(default=dict)
    after_values = models.JSONField(default=dict)
    reason = models.TextField()

    class Meta:
        db_table = "business_change_history"
        constraints = [
            models.UniqueConstraint(
                fields=["target", "sequence_no"],
                name="uq_business_change_history_seq",
            ),
            models.CheckConstraint(
                condition=Q(on_behalf_of__isnull=True) | ~Q(on_behalf_of=F("created_by")),
                name="ck_business_change_history_on_behalf_of",
            ),
        ]


class TimelineEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    event = models.OneToOneField(
        "notifications.BusinessEvent", models.PROTECT, related_name="timeline_event"
    )
    property = models.ForeignKey(
        "properties.Property", models.PROTECT, null=True, blank=True, related_name="timeline_events"
    )
    property_unit = models.ForeignKey(
        "properties.PropertyUnit",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="timeline_events",
    )
    tenancy = models.ForeignKey(
        "tenancies.Tenancy", models.PROTECT, null=True, blank=True, related_name="timeline_events"
    )
    event_at = models.DateTimeField()
    title = models.CharField(max_length=200)

    class Meta:
        db_table = "timeline_events"
        indexes = [
            models.Index(fields=["property_unit", "event_at"], name="ix_timeline_events_unit"),
        ]
