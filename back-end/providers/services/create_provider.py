from django.db import transaction

from providers.models import ServiceProvider
from providers.services.get_provider import get_provider
from providers.services.shared.provider_links import sync_categories, sync_property_links
from providers.services.shared.provider_rules import (
    ensure_reachable,
    find_categories,
    find_owned_properties,
    split_fields,
)


@transaction.atomic
def create_provider(*, actor, fields):
    details = split_fields(fields)
    ensure_reachable(details)
    categories = find_categories(fields.get("category_codes", []))
    links = fields.get("properties", [])
    properties = find_owned_properties(actor, links)
    provider = ServiceProvider.objects.create(owner=actor, created_by=actor, **details)
    sync_categories(provider, categories, actor)
    sync_property_links(provider, links, properties, actor)
    return get_provider(owner=actor, provider_id=provider.pk)
