from communications.services.shared.queries import all_requests, find_or_404


def get_any_contact_request(*, request_id):
    return find_or_404(all_requests(), request_id)
