from django.db import transaction
from django.utils import timezone

from reviews.models import ReviewDecisionType, ReviewStatus
from reviews.services.shared import notices
from reviews.services.shared.acceptance import accept_version
from reviews.services.shared.acting import owner_acted_for
from reviews.services.shared.decisions import (
    finish,
    record_decision,
    require_pending,
    was_already_decided,
)
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import find_evidence_I_answer, reloaded


@transaction.atomic
def approve_evidence(*, user, request_id, idempotency_key, as_admin=False):
    request = find_evidence_I_answer(user, request_id, lock=True, as_admin=as_admin)
    on_behalf_of = owner_acted_for(request, as_admin=as_admin)
    if was_already_decided(request, idempotency_key):
        return request
    require_pending(request)
    version = request.current_submission.proposed_condition_version
    now = timezone.now()
    decision = record_decision(request, user, ReviewDecisionType.APPROVE, None, idempotency_key)
    accept_version(request, user, version, "Approved by the landlord", on_behalf_of=on_behalf_of)
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
        on_behalf_of=on_behalf_of,
    )
    notices.approved(request, version.title)
    return reloaded(request)
