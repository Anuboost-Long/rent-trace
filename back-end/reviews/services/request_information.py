from django.db import transaction

from reviews.models import ReviewDecisionType, ReviewStatus
from reviews.services.shared import notices
from reviews.services.shared.decisions import (
    move,
    record_decision,
    require_pending,
    was_already_decided,
)
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import find_evidence_I_answer, reloaded


@transaction.atomic
def request_information(*, user, request_id, reason, idempotency_key):
    request = find_evidence_I_answer(user, request_id, lock=True)
    if was_already_decided(request, idempotency_key):
        return reloaded(request)
    require_pending(request)
    reason = reason.strip()
    decision = record_decision(
        request, user, ReviewDecisionType.REQUEST_INFORMATION, reason, idempotency_key
    )
    move(request, ReviewStatus.NEEDS_INFORMATION, user)
    record_transition(
        request,
        ReviewStatus.NEEDS_INFORMATION,
        "REQUEST_INFORMATION",
        user,
        reason,
        from_status=ReviewStatus.PENDING_REVIEW,
        submission=request.current_submission,
        decision=decision,
    )
    notices.information_requested(
        request, request.current_submission.proposed_condition_version.title, reason
    )
    return reloaded(request)
