from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound

from providers.models import PropertyServiceProvider, ServiceProvider, ServiceProviderCategory
from providers.services.shared.provider_links import soft_delete


@transaction.atomic
def delete_provider(*, actor, provider_id):
    provider = (
        ServiceProvider.objects.live()
        .owned_by(actor)
        .select_for_update()
        .filter(pk=provider_id)
        .first()
    )
    if provider is None:
        raise NotFound("No provider with this id.")
    now = timezone.now()
    for model in (PropertyServiceProvider, ServiceProviderCategory):
        for link in model.objects.filter(service_provider=provider, deleted_at__isnull=True):
            soft_delete(link, actor, now)
    soft_delete(provider, actor, now)
