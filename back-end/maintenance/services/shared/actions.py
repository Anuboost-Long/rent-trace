from common.models import PartySide
from maintenance.models import MaintenanceStatus
from maintenance.services.shared.parties import current_tenant_users, side_of


def allowed_actions(issue, user):
    """What this person can do with the issue right now. One place decides, and the screens follow it."""
    side = side_of(user, issue)
    if side is None or issue.status == MaintenanceStatus.CLOSED:
        return []
    proposal = issue.open_closure_proposal
    if proposal is not None:
        return _answer_actions(proposal, user, side)
    extra = _landlord_actions(issue) if side == PartySide.LANDLORD else []
    return [*extra, "PROPOSE_CLOSURE"]


def _landlord_actions(issue):
    actions = []
    if issue.status == MaintenanceStatus.REPORTED:
        actions.append("ACKNOWLEDGE")
    if issue.status == MaintenanceStatus.ACKNOWLEDGED:
        actions.append("START")
    actions.append("ASSIGN_PROVIDER")
    current = issue.assignments.filter(superseded_by__isnull=True).first()
    if current is not None and current.completed_at is None:
        actions.append("COMPLETE_VISIT")
    if not current_tenant_users(issue):
        actions.append("CLOSE_VACANT")
    return actions


def _answer_actions(proposal, user, side):
    if proposal.proposed_by_id == user.pk:
        return ["WITHDRAW_CLOSURE"]
    if proposal.proposer_side != side:
        return ["APPROVE_CLOSURE", "REJECT_CLOSURE"]
    return []
