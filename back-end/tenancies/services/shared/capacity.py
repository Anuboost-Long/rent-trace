from rest_framework.exceptions import ValidationError

from tenancies.models import TenancyParty


def check_room(tenancy):
    """A unit may cap how many people live there; people who are only invited don't count yet."""
    limit = tenancy.property_unit.max_occupants
    if limit is None:
        return
    if TenancyParty.objects.filter(tenancy=tenancy).current().count() >= limit:
        raise ValidationError({"unit": f"This unit is full (up to {limit} people)."})
