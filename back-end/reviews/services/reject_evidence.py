from django.db import transaction
from django.utils import timezone

from common.models import PartySide
from reviews.models import ReviewDecisionType, ReviewRoute, ReviewStatus
from reviews.services.shared import notices
from reviews.services.shared.acting import owner_acted_for
from reviews.services.shared.decisions import (
    finish,
    record_decision,
    require_pending,
    was_already_decided,
)
from reviews.services.shared.disputes import open_dispute
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import find_evidence_I_answer, reloaded


@transaction.atomic
def reject_evidence(*, user, request_id, reason, idempotency_key, as_admin=False):
    """Rejecting marks the request disputed and opens the linked dispute case."""
    request = find_evidence_I_answer(user, request_id, lock=True, as_admin=as_admin)
    on_behalf_of = owner_acted_for(request, as_admin=as_admin)
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
        on_behalf_of=on_behalf_of,
    )
    open_dispute(
        request,
        user,
        reason,
        now,
        side=PartySide.LANDLORD,
        route=ReviewRoute.OPPOSITE_SIDE,
        on_behalf_of=on_behalf_of,
    )
    notices.rejected(request, request.current_submission.proposed_condition_version.title, reason)
    return reloaded(request)
