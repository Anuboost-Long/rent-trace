from django.db import transaction
from django.utils import timezone

from maintenance.models import MaintenanceStatus, MaintenanceTrigger
from maintenance.services.shared import notices
from maintenance.services.shared.history import bump, record_transition
from maintenance.services.shared.rules import require_landlord, require_open, require_status
from maintenance.services.shared.scope import find_issue


@transaction.atomic
def start_work(*, user, issue_id):
    issue = find_issue(user, issue_id, lock=True)
    require_landlord(issue, user)
    require_open(issue)
    require_status(issue, {MaintenanceStatus.ACKNOWLEDGED})
    issue.status = MaintenanceStatus.IN_PROGRESS
    issue.work_started_at = timezone.now()
    bump(issue, user)
    record_transition(
        issue,
        MaintenanceStatus.IN_PROGRESS,
        MaintenanceTrigger.CONFIRM_START,
        user,
        "Work started",
        from_status=MaintenanceStatus.ACKNOWLEDGED,
    )
    notices.started(issue)
    return issue
