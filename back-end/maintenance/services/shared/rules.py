from rest_framework.exceptions import PermissionDenied, ValidationError

from common.models import PartySide
from maintenance.models import MaintenanceStatus
from maintenance.services.shared.parties import side_of

CLOSED = "This issue is closed."
WAITING_ON_CLOSURE = "Answer the closure proposal first."
LANDLORD_ONLY = "Only the landlord can do this."


def require_landlord(issue, user):
    if side_of(user, issue) != PartySide.LANDLORD:
        raise PermissionDenied(LANDLORD_ONLY)


def require_open(issue):
    if issue.status == MaintenanceStatus.CLOSED:
        raise ValidationError({"status": CLOSED})
    if issue.open_closure_proposal_id is not None:
        raise ValidationError({"status": WAITING_ON_CLOSURE})


def require_status(issue, allowed):
    if issue.status not in allowed:
        raise ValidationError(
            {
                "status": f"This issue is {issue.status.lower().replace('_', ' ')}, so it can't move that way."
            }
        )
