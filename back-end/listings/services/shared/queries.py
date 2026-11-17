from decimal import Decimal

from django.db.models import Case, Count, DecimalField, F, Min, Prefetch, Q, Value, When

from properties.models import (
    ListingStatus,
    OccupancyStatus,
    Property,
    PropertyFile,
    PropertyFileKind,
    PropertyOwner,
    PropertyStatus,
    PropertyUnit,
)

LISTED = [ListingStatus.AVAILABLE, ListingStatus.PARTIALLY_AVAILABLE]
AVAILABLE_OCCUPANCY = [OccupancyStatus.VACANT, OccupancyStatus.PARTIALLY_OCCUPIED]
PUBLIC_UNIT = Q(
    units__is_public=True,
    units__deleted_at__isnull=True,
    units__occupancy_status__in=AVAILABLE_OCCUPANCY,
)

WEEKLY_RENT = Case(
    When(units__rent_frequency="WEEKLY", then=F("units__rent_amount")),
    When(units__rent_frequency="FORTNIGHTLY", then=F("units__rent_amount") / Value(Decimal(2))),
    When(
        units__rent_frequency="MONTHLY",
        then=F("units__rent_amount") * Value(Decimal(12)) / Value(Decimal(52)),
    ),
    output_field=DecimalField(max_digits=14, decimal_places=4),
)


def listed_properties():
    """Only properties an owner or admin has listed, with at least one available public unit."""
    return (
        Property.objects.filter(
            deleted_at__isnull=True,
            property_status=PropertyStatus.ACTIVE,
            listing_status__in=LISTED,
        )
        .annotate(
            public_unit_count=Count("units", filter=PUBLIC_UNIT, distinct=True),
            weekly_rent=Min(WEEKLY_RENT, filter=PUBLIC_UNIT),
        )
        .filter(public_unit_count__gt=0)
    )


def with_public_details(properties):
    return properties.prefetch_related(
        Prefetch(
            "owners",
            queryset=PropertyOwner.objects.filter(
                is_primary_owner=True, valid_to__isnull=True, deleted_at__isnull=True
            ).select_related("owner"),
            to_attr="primary_owners",
        ),
        Prefetch(
            "units",
            queryset=PropertyUnit.objects.filter(
                is_public=True, deleted_at__isnull=True, occupancy_status__in=AVAILABLE_OCCUPANCY
            ).order_by("id"),
            to_attr="public_units",
        ),
        Prefetch(
            "files",
            queryset=PropertyFile.objects.filter(
                kind=PropertyFileKind.PHOTO, deleted_at__isnull=True
            )
            .select_related("file")
            .order_by("-is_cover", "sort_order", "id"),
            to_attr="photo_files",
        ),
    )
