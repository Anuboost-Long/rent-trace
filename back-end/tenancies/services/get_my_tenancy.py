from rest_framework.exceptions import NotFound

from tenancies.services.shared.my_tenancies import my_tenancies


def get_my_tenancy(*, user, tenancy_id):
    found = my_tenancies(user).filter(pk=tenancy_id).first()
    if found is None:
        raise NotFound("No tenancy with this id.")
    return found
