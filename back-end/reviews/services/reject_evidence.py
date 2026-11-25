import uuid

from django.db import transaction
from django.utils import timezone

from common.models import PartySide
from reviews.models import (
    Dispute,
    ReviewDecisionType,
    ReviewKind,
    ReviewRequest,
    ReviewRoute,
    ReviewStatus,
)
from reviews.services.shared import notices
from reviews.services.shared.decisions import (
    finish,
    record_decision,
    require_pending,
    was_already_decided,
)
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import find_evidence_I_answer, reloaded


@transaction.atomic
def reject_evidence(*, user, request_id, reason, idempotency_key):
    """Rejecting marks the request disputed and opens the linked dispute case."""
    request = find_evidence_I_answer(user, request_id, lock=True)
    if was_already_decided(request, idempotency_key):
        return request
    require_pending(request)
    now = timezone.now()
    reason = reason.strip()
    decision = record_decision(request, user, ReviewDecisionType.REJECT, reason, idempotency_key)
    finish(request, ReviewStatus.DISPUTED, user, now=now)
    record_transition(
        request,
        ReviewStatus.DISPUTED,
        "REJECT",
        user,
        reason,
        from_status=ReviewStatus.PENDING_REVIEW,
        submission=request.current_submission,
        decision=decision,
    )
    open_dispute(request, user, reason, now)
    notices.rejected(request, request.current_submission.proposed_condition_version.title, reason)
    return reloaded(request)


def open_dispute(request, opener, reason, now):
    case = ReviewRequest.objects.create(
        target=request.target,
        kind=ReviewKind.DISPUTE,
        requested_by=opener,
        requester_side=PartySide.LANDLORD,
        review_route=ReviewRoute.OPPOSITE_SIDE,
        status=ReviewStatus.PENDING_REVIEW,
        parent_request=request,
        submitted_at=now,
        created_by=opener,
        updated_by=opener,
    )
    Dispute.objects.create(
        request=case,
        origin_request=request,
        opened_by=opener,
        disputed_submission=request.current_submission,
        details=reason,
        created_by=opener,
        correlation_id=uuid.uuid4(),
    )
    record_transition(case, ReviewStatus.PENDING_REVIEW, "OPEN_DISPUTE", opener, reason)
