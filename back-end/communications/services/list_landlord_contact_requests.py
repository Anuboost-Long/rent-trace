from communications.services.shared.queries import landlord_requests


def list_landlord_contact_requests(*, landlord, status=None):
    requests = landlord_requests(landlord).order_by("-id")
    return requests.with_status(status) if status else requests
