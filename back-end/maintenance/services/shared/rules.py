from rest_framework.exceptions import PermissionDenied, ValidationError

from common.models import PartySide
from maintenance.models import MaintenanceStatus
from maintenance.services.shared.parties import primary_owner_user, side_of

CLOSED = "This issue is closed."
WAITING_ON_CLOSURE = "Answer the closure proposal first."
LANDLORD_ONLY = "Only the landlord can do this."
NO_OWNER = "This property has no primary owner to act for."


def require_landlord(issue, user):
    if side_of(user, issue) != PartySide.LANDLORD:
        raise PermissionDenied(LANDLORD_ONLY)


def acting_landlord(issue, user, *, as_admin=False):
    """Checks the person may do a landlord's action. Returns the owner an admin is acting for,
    or None when the person is the landlord themselves."""
    if side_of(user, issue) == PartySide.LANDLORD:
        return None
    if not as_admin:
        raise PermissionDenied(LANDLORD_ONLY)
    owner = primary_owner_user(issue)
    if owner is None:
        raise ValidationError({"status": NO_OWNER})
    return owner


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
