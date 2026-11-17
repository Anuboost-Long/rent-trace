from tenancies.services.shared.my_tenancies import my_tenancies


def list_my_tenancies(*, user):
    return list(my_tenancies(user))
