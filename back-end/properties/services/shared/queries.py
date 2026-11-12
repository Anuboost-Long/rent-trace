from django.db.models import Count, Prefetch, Q

from properties.models import Property, PropertyFile, PropertyOwner, PropertyUnit


def live_properties(owned_by=None):
    properties = Property.objects.filter(deleted_at__isnull=True)
    if owned_by is None:
        return properties
    owned = PropertyOwner.objects.filter(
        owner=owned_by, valid_to__isnull=True, deleted_at__isnull=True
    )
    return properties.filter(pk__in=owned.values("property_id"))


def with_owners_and_units(properties):
    current_owners = PropertyOwner.objects.filter(
        valid_to__isnull=True, deleted_at__isnull=True
    ).select_related("owner")
    return properties.annotate(
        unit_count=Count("units", filter=Q(units__deleted_at__isnull=True))
    ).prefetch_related(
        Prefetch(
            "owners",
            queryset=current_owners.order_by("-is_primary_owner", "id"),
            to_attr="current_owners",
        ),
        Prefetch(
            "files",
            queryset=PropertyFile.objects.filter(deleted_at__isnull=True)
            .select_related("file")
            .order_by("sort_order", "id"),
            to_attr="active_files",
        ),
        Prefetch(
            "units",
            queryset=PropertyUnit.objects.filter(deleted_at__isnull=True).order_by("id"),
            to_attr="active_units",
        ),
    )


def current_owner_users(place):
    current = PropertyOwner.objects.filter(
        property=place, valid_to__isnull=True, deleted_at__isnull=True
    ).select_related("owner")
    return [row.owner for row in current]
