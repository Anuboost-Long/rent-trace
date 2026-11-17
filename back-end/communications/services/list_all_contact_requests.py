from communications.services.shared.queries import all_requests


def list_all_contact_requests(*, status=None, q=None):
    requests = all_requests().order_by("-id")
    if status:
        requests = requests.with_status(status)
    if q:
        requests = requests.matching(q)
    return requests
