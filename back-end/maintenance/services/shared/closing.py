import uuid

from django.utils import timezone

from maintenance.models import ClosureDecision, MaintenanceClosureResponse, MaintenanceStatus
from maintenance.services.shared.history import bump, record_transition


def answer_proposal(proposal, decision, responder, reason=None):
    return MaintenanceClosureResponse.objects.create(
        proposal=proposal,
        decision=decision,
        responded_by=responder,
        reason=reason,
        created_by=responder,
        correlation_id=uuid.uuid4(),
    )


def close_issue(issue, outcome, trigger, actor, reason, *, proposal=None, on_behalf_of=None):
    previous = issue.status
    issue.status = MaintenanceStatus.CLOSED
    issue.closed_at = timezone.now()
    issue.closure_outcome = outcome
    issue.open_closure_proposal = None
    bump(issue, actor)
    record_transition(
        issue,
        MaintenanceStatus.CLOSED,
        trigger,
        actor,
        reason,
        from_status=previous,
        proposal=proposal,
        on_behalf_of=on_behalf_of,
    )


def clear_open_proposal(issue, decision, responder, reason=None):
    answer_proposal(issue.open_closure_proposal, decision, responder, reason)
    issue.open_closure_proposal = None
    bump(issue, responder)


__all__ = ["ClosureDecision", "answer_proposal", "clear_open_proposal", "close_issue"]
