from django.db import transaction

from communications.models import ContactRequestStatus
from communications.services.shared import notices
from communications.services.shared.queries import find_or_404, tenant_requests
from communications.services.shared.transitions import move_to


@transaction.atomic
def cancel_contact_request(*, tenant, request_id):
    found = find_or_404(tenant_requests(tenant), request_id, lock=True)
    move_to(found, ContactRequestStatus.CANCELLED, tenant)
    notices.request_cancelled(found)
    return found
