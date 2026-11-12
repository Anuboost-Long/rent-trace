from rest_framework.exceptions import NotFound

from communications.models import ContactRequest
from properties.services.shared.queries import live_properties

NOT_FOUND = "No contact request with this id."


def tenant_requests(tenant):
    return ContactRequest.objects.live().filter(tenant=tenant).with_details()


def landlord_requests(landlord):
    return (
        ContactRequest.objects.live().filter(property__in=live_properties(landlord)).with_details()
    )


def find_or_404(requests, request_id, *, lock=False):
    if lock:
        requests = requests.select_for_update(of=("self",))
    found = requests.filter(pk=request_id).first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found
