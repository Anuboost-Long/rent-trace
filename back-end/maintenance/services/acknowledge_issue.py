from django.db import transaction
from django.utils import timezone

from maintenance.models import MaintenanceStatus, MaintenanceTrigger
from maintenance.services.shared import notices
from maintenance.services.shared.history import bump, record_transition
from maintenance.services.shared.rules import acting_landlord, require_open, require_status
from maintenance.services.shared.scope import find_issue


@transaction.atomic
def acknowledge_issue(*, user, issue_id, as_admin=False):
    issue = find_issue(user, issue_id, lock=True, as_admin=as_admin)
    on_behalf_of = acting_landlord(issue, user, as_admin=as_admin)
    require_open(issue)
    require_status(issue, {MaintenanceStatus.REPORTED})
    issue.status = MaintenanceStatus.ACKNOWLEDGED
    issue.acknowledged_at = timezone.now()
    bump(issue, user)
    record_transition(
        issue,
        MaintenanceStatus.ACKNOWLEDGED,
        MaintenanceTrigger.OPPOSITE_OPEN,
        user,
        "Acknowledged by the landlord",
        from_status=MaintenanceStatus.REPORTED,
        on_behalf_of=on_behalf_of,
    )
    notices.acknowledged(issue)
    return issue
