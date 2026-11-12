from rest_framework.exceptions import NotFound

from tenancies.services.shared.invitations import live_tenancies


def get_tenancy(*, tenancy_id, owned_by=None):
    found = live_tenancies(owned_by).with_parties_and_invitations().filter(pk=tenancy_id).first()
    if found is None:
        raise NotFound("No tenancy with this id.")
    return found
