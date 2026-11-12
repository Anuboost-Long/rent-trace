from django.utils import timezone
from rest_framework.exceptions import ValidationError

from communications.models import ContactRequestStatus as Status

ALLOWED_FROM = {
    Status.ACCEPTED: {Status.PENDING},
    Status.DECLINED: {Status.PENDING},
    Status.CANCELLED: {Status.PENDING},
    Status.REVOKED: {Status.ACCEPTED},
}


def move_to(contact_request, new_status, actor):
    if contact_request.status not in ALLOWED_FROM[new_status]:
        raise ValidationError(
            {"status": f"This request is {contact_request.status.lower()}, so it can't be changed."}
        )
    contact_request.status = new_status
    contact_request.decided_at = timezone.now()
    contact_request.decided_by = actor
    contact_request.updated_by = actor
    contact_request.row_version += 1
    contact_request.save()
