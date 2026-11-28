import uuid

from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from common.models import PartySide
from maintenance.models import MaintenanceClosureProposal
from maintenance.services.shared import notices
from maintenance.services.shared.history import bump
from maintenance.services.shared.parties import other_side_users, side_of
from maintenance.services.shared.rules import acting_landlord, require_open
from maintenance.services.shared.scope import find_issue

NOT_A_PARTY = "Only the tenants and the landlord can close an issue."


@transaction.atomic
def propose_closure(*, user, issue_id, outcome, reason, as_admin=False):
    issue = find_issue(user, issue_id, lock=True, as_admin=as_admin)
    side = side_of(user, issue)
    if side is None and as_admin:
        acting_landlord(issue, user, as_admin=True)
        side = PartySide.LANDLORD
    if side is None:
        raise PermissionDenied(NOT_A_PARTY)
    require_open(issue)
    next_version = issue.row_version + 1
    proposal = MaintenanceClosureProposal.objects.create(
        maintenance_issue=issue,
        outcome=outcome,
        reason=reason.strip(),
        proposed_by=user,
        proposer_side=side,
        issue_row_version=next_version,
        created_by=user,
        correlation_id=uuid.uuid4(),
    )
    issue.open_closure_proposal = proposal
    bump(issue, user)
    notices.closure_proposed(issue, user, other_side_users(issue, side))
    return issue
