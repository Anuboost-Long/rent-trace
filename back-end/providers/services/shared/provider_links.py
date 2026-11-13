from django.utils import timezone

from providers.models import PropertyServiceProvider, ServiceProviderCategory


def soft_delete(record, actor, now):
    record.deleted_at = now
    record.deleted_by = actor
    record.updated_by = actor
    record.row_version += 1
    record.save()


def sync_categories(provider, categories, actor):
    now = timezone.now()
    wanted = {category.pk: category for category in categories}
    current = ServiceProviderCategory.objects.filter(
        service_provider=provider, deleted_at__isnull=True
    )
    for link in current:
        if link.service_category_id in wanted:
            del wanted[link.service_category_id]
        else:
            soft_delete(link, actor, now)
    for category in wanted.values():
        ServiceProviderCategory.objects.create(
            service_provider=provider, service_category=category, created_by=actor
        )


def sync_property_links(provider, links, properties, actor):
    now = timezone.now()
    wanted = {link["property_id"]: link for link in links}
    current = PropertyServiceProvider.objects.filter(
        service_provider=provider, deleted_at__isnull=True
    )
    for link in current:
        change = wanted.pop(link.property_id, None)
        if change is None:
            soft_delete(link, actor, now)
            continue
        link.is_recommended = change["is_recommended"]
        link.contract_notes = change.get("contract_notes") or None
        link.updated_by = actor
        link.row_version += 1
        link.save()
    for property_id, change in wanted.items():
        PropertyServiceProvider.objects.create(
            property=properties[property_id],
            service_provider=provider,
            is_recommended=change["is_recommended"],
            contract_notes=change.get("contract_notes") or None,
            created_by=actor,
        )
