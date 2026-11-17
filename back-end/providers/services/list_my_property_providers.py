from django.db.models import F

from providers.models import ServiceProvider
from tenancies.services import get_my_tenancy
from tenancies.services.shared.invitations import CLOSED_STATUSES


def list_my_property_providers(*, user, tenancy_id):
    tenancy = get_my_tenancy(user=user, tenancy_id=tenancy_id)
    still_living_there = (
        tenancy.my_parties[0].left_at is None and tenancy.status not in CLOSED_STATUSES
    )
    if not still_living_there:
        return []
    return (
        ServiceProvider.objects.live()
        .filter(
            property_links__property=tenancy.property_unit.property_id,
            property_links__deleted_at__isnull=True,
        )
        .annotate(is_recommended=F("property_links__is_recommended"))
        .with_categories()
        .order_by("-is_recommended", "business_name", "id")
    )
