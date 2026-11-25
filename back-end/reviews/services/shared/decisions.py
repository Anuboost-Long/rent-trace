import uuid

from rest_framework.exceptions import ValidationError

from reviews.models import ReviewDecision, ReviewerSide, ReviewStatus

NOT_PENDING = "This has already been answered or withdrawn."
KEY_USED = "That idempotency key was already used for a different request."


def was_already_decided(request, idempotency_key):
    """True when this exact answer was recorded before, so a retry changes nothing."""
    earlier = ReviewDecision.objects.filter(idempotency_key=idempotency_key).first()
    if earlier is None:
        return False
    if earlier.request_id != request.pk:
        raise ValidationError({"idempotency_key": KEY_USED})
    return True


def require_pending(request):
    if request.status != ReviewStatus.PENDING_REVIEW:
        raise ValidationError({"request": NOT_PENDING})


def record_decision(request, reviewer, decision, reason, idempotency_key):
    return ReviewDecision.objects.create(
        request=request,
        submission=request.current_submission,
        reviewer=reviewer,
        reviewer_side=ReviewerSide.LANDLORD,
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
