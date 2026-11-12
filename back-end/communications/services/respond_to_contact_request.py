from django.db import transaction

from accounts.services.shared.mail import send_after_commit
from communications.integrations import emails
from communications.models import ContactRequestStatus
from communications.services.shared import notices
from communications.services.shared.presentation import listing_title
from communications.services.shared.queries import find_or_404, landlord_requests
from communications.services.shared.transitions import move_to

TELL_TENANT = {ContactRequestStatus.ACCEPTED, ContactRequestStatus.DECLINED}


@transaction.atomic
def respond_to_contact_request(*, landlord, request_id, new_status):
    found = find_or_404(landlord_requests(landlord), request_id, lock=True)
    move_to(found, new_status, landlord)
    notices.request_answered(found, landlord)
    if new_status in TELL_TENANT:
        send_after_commit(
            emails.send_request_answered,
            found.tenant,
            listing_title(found),
            new_status == ContactRequestStatus.ACCEPTED,
        )
    return found
