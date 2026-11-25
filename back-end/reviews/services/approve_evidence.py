from django.db import transaction
from django.utils import timezone

from reviews.models import ReviewDecisionType, ReviewStatus
from reviews.services.shared import notices
from reviews.services.shared.decisions import (
    finish,
    record_decision,
    require_pending,
    was_already_decided,
)
from reviews.services.shared.history import record_change, record_transition
from reviews.services.shared.scope import find_evidence_I_answer, reloaded


@transaction.atomic
def approve_evidence(*, user, request_id, idempotency_key):
    request = find_evidence_I_answer(user, request_id, lock=True)
    if was_already_decided(request, idempotency_key):
        return request
    require_pending(request)
    note = request.target.condition_record
    version = request.current_submission.proposed_condition_version
    now = timezone.now()
    decision = record_decision(request, user, ReviewDecisionType.APPROVE, None, idempotency_key)
    record_change(
        request,
        user,
        "ACCEPT_CONDITION_VERSION",
        {"accepted_version": None},
        {"accepted_version": version.version_no},
        "Approved by the landlord",
    )
    note.accepted_version = version
    note.updated_by = user
    note.row_version += 1
    note.save()
    finish(request, ReviewStatus.APPROVED, user, now=now, applied=True)
    record_transition(
        request,
        ReviewStatus.APPROVED,
        "APPROVE",
        user,
        "Approved by the landlord",
        from_status=ReviewStatus.PENDING_REVIEW,
        submission=request.current_submission,
        decision=decision,
    )
    notices.approved(request, version.title)
    return reloaded(request)
