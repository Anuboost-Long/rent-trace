import uuid

from django.db.models import Max

from maintenance.models import MaintenanceStatusHistory


def record_transition(
    issue, to_status, trigger, actor, reason, *, from_status=None, proposal=None, on_behalf_of=None
):
    """Writes the status history row for a move. Call it with the issue row locked."""
    last = issue.status_history.aggregate(last=Max("sequence_no"))["last"] or 0
    return MaintenanceStatusHistory.objects.create(
        maintenance_issue=issue,
        sequence_no=last + 1,
        from_status=from_status,
        to_status=to_status,
        trigger=trigger,
        actor=actor,
        on_behalf_of=on_behalf_of,
        closure_proposal=proposal,
        reason=reason,
        created_by=actor,
        correlation_id=uuid.uuid4(),
    )


def bump(issue, actor):
    issue.updated_by = actor
    issue.row_version += 1
    issue.save()
