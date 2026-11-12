import secrets

from rest_framework.exceptions import ValidationError

from properties.models import PropertyUnit
from properties.services.shared.fields import blank_to_none
from properties.services.shared.queries import live_properties
from tenancies.models import Tenancy, TenancyType


def create_tenancy(*, actor, fields, owned_by=None):
    unit = (
        PropertyUnit.objects.filter(deleted_at__isnull=True)
        .filter(property__in=live_properties(owned_by))
        .filter(pk=fields["property_unit_id"])
        .first()
    )
    if unit is None:
        raise ValidationError({"property_unit_id": "No unit with this id."})
    clean = blank_to_none({**fields, "notes": fields.get("notes") or None})
    return Tenancy.objects.create(
        property_unit=unit,
        reference_no=f"T-{secrets.token_hex(6).upper()}",
        tenancy_type=TenancyType.WHOLE_UNIT,
        start_date=clean["start_date"],
        end_date=clean.get("end_date"),
        notes=clean["notes"],
        created_by=actor,
    )
