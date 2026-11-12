from django.db.models import Prefetch

from properties.models import PropertyOwner
from tenancies.models import Tenancy, TenancyParty


def my_tenancies(user):
    """Every tenancy the person has joined, past ones included, newest start first."""
    mine = TenancyParty.objects.filter(tenant=user, deleted_at__isnull=True).order_by("-id")
    housemates = TenancyParty.objects.current().exclude(tenant=user).select_related("tenant")
    owners = (
        PropertyOwner.objects.filter(valid_to__isnull=True, deleted_at__isnull=True)
        .select_related("owner")
        .order_by("-is_primary_owner", "id")
    )
    return (
        Tenancy.objects.live()
        .for_tenant(user)
        .select_related("property_unit__property")
        .prefetch_related(
            Prefetch("parties", queryset=mine, to_attr="my_parties"),
            Prefetch("parties", queryset=housemates.order_by("id"), to_attr="housemates"),
            Prefetch("property_unit__property__owners", queryset=owners, to_attr="current_owners"),
        )
        .order_by("-start_date", "-id")
    )
