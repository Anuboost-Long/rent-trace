from django.db import transaction
from rest_framework.exceptions import NotFound

from providers.models import ServiceProvider
from providers.services.get_provider import get_provider
from providers.services.shared.provider_links import sync_categories, sync_property_links
from providers.services.shared.provider_rules import (
    CONTACT_FIELDS,
    ensure_reachable,
    find_categories,
    find_owned_properties,
    split_fields,
)


@transaction.atomic
def update_provider(*, actor, provider_id, changes):
    provider = (
        ServiceProvider.objects.live()
        .owned_by(actor)
        .select_for_update()
        .filter(pk=provider_id)
        .first()
    )
    if provider is None:
        raise NotFound("No provider with this id.")
    details = split_fields(changes)
    ensure_reachable({name: details.get(name, getattr(provider, name)) for name in CONTACT_FIELDS})
    categories = find_categories(changes["category_codes"]) if "category_codes" in changes else None
    links = changes.get("properties")
    properties = find_owned_properties(actor, links) if links is not None else None
    for name, value in details.items():
        setattr(provider, name, value)
    provider.updated_by = actor
    provider.row_version += 1
    provider.save()
    if categories is not None:
        sync_categories(provider, categories, actor)
    if links is not None:
        sync_property_links(provider, links, properties, actor)
    return get_provider(owner=actor, provider_id=provider.pk)
