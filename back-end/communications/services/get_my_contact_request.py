from communications.services.shared.queries import find_or_404, tenant_requests


def get_my_contact_request(*, tenant, request_id):
    return find_or_404(tenant_requests(tenant), request_id)
