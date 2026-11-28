from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from maintenance.models import ClosureDecision, MaintenanceStatus
from maintenance.services.shared.closing import clear_open_proposal
from maintenance.services.shared.scope import find_issue

NOT_YOURS = "Only the person who proposed it can withdraw it."
NOTHING_OPEN = "There is no open proposal."


@transaction.atomic
def withdraw_closure(*, user, issue_id, as_admin=False):
    issue = find_issue(user, issue_id, lock=True, as_admin=as_admin)
    proposal = issue.open_closure_proposal
    if issue.status == MaintenanceStatus.CLOSED or proposal is None:
        raise ValidationError({"proposal": NOTHING_OPEN})
    if proposal.proposed_by_id != user.pk:
        raise PermissionDenied(NOT_YOURS)
    clear_open_proposal(issue, ClosureDecision.WITHDRAWN, user)
    return issue
