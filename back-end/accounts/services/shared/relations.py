from accounts.models import User
from properties.services.shared.queries import live_properties
from tenancies.models import Tenancy, TenancyParty


def shares_a_tenancy(viewer, target):
    """Housemates, a tenant and the landlord of their property, in either direction."""
    mine = TenancyParty.objects.filter(tenant=viewer).values("tenancy_id")
    housemates = TenancyParty.objects.filter(tenant=target, tenancy_id__in=mine).exists()
    owns_my_property = (
        Tenancy.objects.filter(
            pk__in=mine,
            property_unit__property__owners__owner=target,
            property_unit__property__owners__valid_to__isnull=True,
        )
        .distinct()
        .exists()
    )
    is_my_tenant = TenancyParty.objects.filter(
        tenant=target, tenancy__property_unit__property__in=live_properties(viewer)
    ).exists()
    return housemates or owns_my_property or is_my_tenant


def may_see_picture(viewer, target: User, *, viewer_is_admin: bool):
    return viewer.pk == target.pk or viewer_is_admin or shares_a_tenancy(viewer, target)
