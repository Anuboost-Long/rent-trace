from django.db import transaction
from rest_framework.exceptions import ValidationError

from providers.models import PropertyServiceProvider, ServiceProvider
from providers.services.shared.property_links import find_owned_property, providers_on


@transaction.atomic
def link_providers(*, actor, property_id, provider_ids):
    property_ = find_owned_property(actor, property_id)
    wanted = set(provider_ids)
    mine = ServiceProvider.objects.live().owned_by(actor).filter(pk__in=wanted)
    unknown = wanted - {provider.pk for provider in mine}
    if unknown:
        raise ValidationError(
            {"provider_ids": f"Not your tradespeople: {', '.join(map(str, sorted(unknown)))}."}
        )
    already = set(
        PropertyServiceProvider.objects.filter(
            property=property_, service_provider__in=mine, deleted_at__isnull=True
        ).values_list("service_provider_id", flat=True)
    )
    for provider in mine.exclude(pk__in=already):
        PropertyServiceProvider.objects.create(
            property=property_, service_provider=provider, created_by=actor
        )
    return providers_on(actor, property_)
