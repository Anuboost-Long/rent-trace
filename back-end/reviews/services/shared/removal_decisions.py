from django.utils import timezone

from properties.services.shared.queries import current_owner_users
from reviews.models import ReviewDecisionType, ReviewerSide, ReviewStatus
from reviews.services.shared import notices
from reviews.services.shared.decisions import (
    finish,
    record_decision,
    require_pending,
    was_already_decided,
)
from reviews.services.shared.history import record_transition
from reviews.services.shared.removals import apply_removal


def decide_removal(admin, request, *, approve, reason, idempotency_key):
    if was_already_decided(request, idempotency_key):
        return request
    require_pending(request)
    now = timezone.now()
    kind = ReviewDecisionType.APPROVE if approve else ReviewDecisionType.REJECT
    decision = record_decision(
        request, admin, kind, reason, idempotency_key, side=ReviewerSide.ADMIN
    )
    if approve:
        apply_removal(request, admin, reason, now)
    status = ReviewStatus.APPROVED if approve else ReviewStatus.REJECTED
    finish(request, status, admin, now=now, applied=approve)
    record_transition(
        request,
        status,
        "ADMIN_APPROVE" if approve else "ADMIN_REJECT",
        admin,
        reason,
        from_status=ReviewStatus.PENDING_REVIEW,
        submission=request.current_submission,
        decision=decision,
    )
    place = request.target.condition_record.property_unit.property
    notices.removal_decided(
        request, current_owner_users(place), "approved" if approve else "rejected", reason
    )
    return request
