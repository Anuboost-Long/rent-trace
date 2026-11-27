import uuid

from django.db.models import Max

from history.models import BusinessChangeHistory
from reviews.models import ReviewStatusHistory


def record_transition(
    request,
    to_status,
    action,
    actor,
    reason,
    *,
    from_status=None,
    submission=None,
    decision=None,
    on_behalf_of=None,
):
    """Writes the status history row for a move. Call it with the request row locked."""
    last = request.status_history.aggregate(last=Max("sequence_no"))["last"] or 0
    return ReviewStatusHistory.objects.create(
        request=request,
        sequence_no=last + 1,
        from_status=from_status,
        to_status=to_status,
        action=action,
        actor=actor,
        on_behalf_of=on_behalf_of,
        submission=submission,
        decision=decision,
        reason=reason,
        created_by=actor,
        correlation_id=uuid.uuid4(),
    )


def record_change(
    request, actor, action, before_values, after_values, reason, *, on_behalf_of=None
):
    last = request.target.change_history.aggregate(last=Max("sequence_no"))["last"] or 0
    return BusinessChangeHistory.objects.create(
        target=request.target,
        sequence_no=last + 1,
        request=request,
        action=action,
        before_values=before_values,
        after_values=after_values,
        reason=reason,
        on_behalf_of=on_behalf_of,
        created_by=actor,
        correlation_id=uuid.uuid4(),
    )
