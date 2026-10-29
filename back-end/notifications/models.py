from django.db import models
from django.db.models import F, Q

from common.models import EventRecord, enum_check


class DeliveryChannel(models.TextChoices):
    EMAIL = "EMAIL"


class DeliveryStatus(models.TextChoices):
    QUEUED = "QUEUED"
    SENDING = "SENDING"
    SENT = "SENT"
    RETRY = "RETRY"
    FAILED = "FAILED"
    SUPPRESSED = "SUPPRESSED"


class AttemptOutcome(models.TextChoices):
    SENT = "SENT"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    SUPPRESSED = "SUPPRESSED"


class BusinessEvent(EventRecord):
    event_key = models.UUIDField(unique=True)
    event_type = models.CharField(max_length=80)
    target = models.ForeignKey(
        "reviews.ReviewTarget", models.PROTECT, related_name="business_events"
    )
    request = models.ForeignKey(
        "reviews.ReviewRequest",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="business_events",
    )
    payload = models.JSONField(default=dict)

    class Meta:
        db_table = "business_events"


class Notification(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    event = models.ForeignKey(BusinessEvent, models.PROTECT, related_name="notifications")
    recipient = models.ForeignKey("accounts.User", models.PROTECT, related_name="notifications")
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_suppressed = models.BooleanField(default=False)

    class Meta:
        db_table = "notifications"
        constraints = [
            models.UniqueConstraint(
                fields=["event", "recipient"], name="uq_notifications_recipient"
            ),
        ]
        indexes = [
            models.Index(
                fields=["recipient", "read_at", "created_at"],
                name="ix_notifications_inbox",
            ),
        ]


class NotificationDelivery(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notification = models.ForeignKey(Notification, models.PROTECT, related_name="deliveries")
    channel = models.TextField(choices=DeliveryChannel, default=DeliveryChannel.EMAIL)
    status = models.TextField(choices=DeliveryStatus, default=DeliveryStatus.QUEUED)
    recipient_email = models.CharField(max_length=255)
    attempt_count = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    lease_until = models.DateTimeField(null=True, blank=True)
    provider_message_id = models.CharField(max_length=255, null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notification_deliveries"
        constraints = [
            enum_check("notification_deliveries", "channel", DeliveryChannel),
            enum_check("notification_deliveries", "status", DeliveryStatus),
            models.UniqueConstraint(
                fields=["notification", "channel"],
                name="uq_notification_deliveries_channel",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "next_attempt_at"], name="ix_deliveries_due"),
        ]


class NotificationDeliveryAttempt(EventRecord):
    delivery = models.ForeignKey(NotificationDelivery, models.PROTECT, related_name="attempts")
    attempt_no = models.PositiveIntegerField()
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    outcome = models.TextField(choices=AttemptOutcome)
    error_code = models.CharField(max_length=100, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "notification_delivery_attempts"
        constraints = [
            enum_check("notification_delivery_attempts", "outcome", AttemptOutcome),
            models.CheckConstraint(
                condition=Q(finished_at__gte=F("started_at")),
                name="ck_notification_delivery_attempts_period",
            ),
            models.UniqueConstraint(
                fields=["delivery", "attempt_no"],
                name="uq_notification_delivery_attempts_no",
            ),
        ]
