from tenancies.services.shared.invitations import live_tenancies


def list_tenancies(*, q=None, status=None, owned_by=None):
    tenancies = live_tenancies(owned_by)
    if q:
        tenancies = tenancies.search(q)
    if status:
        tenancies = tenancies.with_status(status)
    return tenancies.with_parties_and_invitations().newest_first()
