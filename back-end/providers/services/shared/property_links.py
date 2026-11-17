from django.db.models import F
from rest_framework.exceptions import NotFound

from properties.services.shared.queries import live_properties
from providers.models import PropertyServiceProvider, ServiceProvider


def find_owned_property(owner, property_id):
    found = live_properties(owner).filter(pk=property_id).first()
    if found is None:
        raise NotFound("No property with this id.")
    return found


def live_link(property_, provider_id):
    return PropertyServiceProvider.objects.filter(
        property=property_,
        service_provider_id=provider_id,
        service_provider__deleted_at__isnull=True,
        deleted_at__isnull=True,
    )


def providers_on(owner, property_):
    return (
        ServiceProvider.objects.live()
        .owned_by(owner)
        .filter(property_links__property=property_, property_links__deleted_at__isnull=True)
        .annotate(
            is_recommended=F("property_links__is_recommended"),
            contract_notes=F("property_links__contract_notes"),
        )
        .with_categories()
        .order_by("-is_recommended", "business_name", "id")
    )
