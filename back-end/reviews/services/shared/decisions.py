import uuid
from datetime import timedelta

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from reviews.models import ReviewDecision, ReviewerSide, ReviewKind, ReviewStatus

EVIDENCE_WINDOW = timedelta(days=14)
NOT_PENDING = "This has already been answered or withdrawn."
EXPIRED = "This report expired after 14 days. The tenant can send a new one."
KEY_USED = "That idempotency key was already used for a different request."


def was_already_decided(request, idempotency_key):
    """True when this exact answer was recorded before, so a retry changes nothing."""
    earlier = ReviewDecision.objects.filter(idempotency_key=idempotency_key).first()
    if earlier is None:
        return False
    if earlier.request_id != request.pk:
        raise ValidationError({"idempotency_key": KEY_USED})
    return True


def is_expired(request):
    """Waiting too long is worked out when it is read; nothing is stored or scheduled."""
    return (
        request.kind == ReviewKind.EVIDENCE_REVIEW
        and request.status == ReviewStatus.PENDING_REVIEW
        and request.submitted_at + EVIDENCE_WINDOW <= timezone.now()
    )


def require_pending(request):
    if request.status != ReviewStatus.PENDING_REVIEW:
        raise ValidationError({"request": NOT_PENDING})
    if is_expired(request):
        raise ValidationError({"request": EXPIRED})


def record_decision(
    request,
    reviewer,
    decision,
    reason,
    idempotency_key,
    *,
    side=ReviewerSide.LANDLORD,
    submission=None,
):
    return ReviewDecision.objects.create(
        request=request,
        submission=submission or request.current_submission,
        reviewer=reviewer,
        reviewer_side=side,
        decision=decision,
        reason=reason,
        idempotency_key=idempotency_key,
        created_by=reviewer,
        correlation_id=uuid.uuid4(),
    )


def finish(request, status, actor, *, now, applied=False):
    request.status = status
    request.completed_at = now
    request.applied_at = now if applied else None
    request.updated_by = actor
    request.row_version += 1
    request.save()
