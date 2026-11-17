from communications.services.shared.queries import find_or_404, landlord_requests


def get_landlord_contact_request(*, landlord, request_id):
    return find_or_404(landlord_requests(landlord), request_id)
