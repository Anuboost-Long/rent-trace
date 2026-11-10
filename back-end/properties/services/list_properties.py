from django.db.models import Q

from properties.models import PropertyOwner
from properties.services.shared.queries import live_properties, with_owners_and_units


def list_properties(*, q=None, status=None, owned_by=None):
    properties = live_properties(owned_by)
    for term in (q or "").split():
        owned_by_match = PropertyOwner.objects.filter(
            valid_to__isnull=True, deleted_at__isnull=True
        ).filter(
            Q(owner__email__icontains=term)
            | Q(owner__first_name__icontains=term)
            | Q(owner__last_name__icontains=term)
        )
        properties = properties.filter(
            Q(property_name__icontains=term)
            | Q(address_line_1__icontains=term)
            | Q(address_line_2__icontains=term)
            | Q(suburb__icontains=term)
            | Q(postcode__icontains=term)
            | Q(pk__in=owned_by_match.values("property_id"))
        )
    if status:
        properties = properties.filter(property_status=status)
    return with_owners_and_units(properties).order_by("-created_at", "-id")
