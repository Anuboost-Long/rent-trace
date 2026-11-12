from django.db import transaction
from rest_framework.exceptions import ValidationError

from maintenance.models import ClosureDecision, MaintenanceStatus, MaintenanceTrigger
from maintenance.services.shared import notices
from maintenance.services.shared.closing import clear_open_proposal, close_issue
from maintenance.services.shared.parties import current_tenant_users
from maintenance.services.shared.rules import CLOSED, require_landlord
from maintenance.services.shared.scope import find_issue

TENANTS_REMAIN = (
    "A tenant still lives here, so closing needs their approval. Propose the closure instead."
)


@transaction.atomic
def close_vacant(*, user, issue_id, outcome, reason):
    """With no current tenant there is nobody to approve, so the landlord closes it directly."""
    issue = find_issue(user, issue_id, lock=True)
    require_landlord(issue, user)
    if issue.status == MaintenanceStatus.CLOSED:
        raise ValidationError({"status": CLOSED})
    if current_tenant_users(issue):
        raise ValidationError({"status": TENANTS_REMAIN})
    if issue.open_closure_proposal_id is not None:
        clear_open_proposal(issue, ClosureDecision.WITHDRAWN, user, "Closed directly")
    close_issue(issue, outcome, MaintenanceTrigger.VACANT_OWNER_CLOSURE, user, reason.strip())
    notices.closed(issue, [issue.reported_by])
    return issue
