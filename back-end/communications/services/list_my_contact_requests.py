from communications.services.shared.queries import tenant_requests


def list_my_contact_requests(*, tenant, status=None):
    requests = tenant_requests(tenant).order_by("-id")
    return requests.with_status(status) if status else requests
