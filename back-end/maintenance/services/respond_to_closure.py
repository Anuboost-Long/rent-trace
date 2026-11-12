from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from maintenance.models import ClosureDecision, MaintenanceStatus, MaintenanceTrigger
from maintenance.services.shared import notices
from maintenance.services.shared.closing import clear_open_proposal, close_issue
from maintenance.services.shared.parties import side_of
from maintenance.services.shared.scope import find_issue

NO_LONGER_OPEN = "This proposal is no longer open."
STALE = "The issue changed since this was proposed. Ask for it again."
OWN = "You can't answer your own proposal."
OTHER_SIDE = "Only the other side can answer this proposal."


@transaction.atomic
def respond_to_closure(*, user, issue_id, proposal_id, decision):
    """The other side approves or rejects an open closure proposal. The issue is locked first."""
    issue = find_issue(user, issue_id, lock=True)
    proposal = issue.open_closure_proposal
    if issue.status == MaintenanceStatus.CLOSED or proposal is None or proposal.pk != proposal_id:
        raise ValidationError({"proposal": NO_LONGER_OPEN})
    side = side_of(user, issue)
    if proposal.proposed_by_id == user.pk:
        raise PermissionDenied(OWN)
    if side is None or side == proposal.proposer_side:
        raise PermissionDenied(OTHER_SIDE)
    if decision == ClosureDecision.REJECTED:
        clear_open_proposal(issue, ClosureDecision.REJECTED, user)
        notices.closure_rejected(issue, proposal.proposed_by, user)
        return issue
    if issue.row_version != proposal.issue_row_version:
        raise ValidationError({"proposal": STALE})
    clear_open_proposal(issue, ClosureDecision.APPROVED, user)
    close_issue(
        issue,
        proposal.outcome,
        MaintenanceTrigger.APPROVED_CLOSURE,
        user,
        proposal.reason,
        proposal=proposal,
    )
    notices.closed(issue, [proposal.proposed_by])
    return issue
