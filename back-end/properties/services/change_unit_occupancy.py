from django.db import transaction
from rest_framework.exceptions import ValidationError

from properties.services.shared.fields import save_changes
from properties.services.shared.units import find_unit_for_update
from tenancies.models import Tenancy

HAS_TENANT = "This unit has a current tenant, so its occupancy is set automatically."


@transaction.atomic
def change_unit_occupancy(*, actor, property_id, unit_id, occupancy_status, owned_by=None):
    unit = find_unit_for_update(property_id, unit_id, owned_by)
    if Tenancy.objects.active_on(unit).exists():
        raise ValidationError({"occupancy_status": HAS_TENANT})
    save_changes(actor, unit, {"occupancy_status": occupancy_status})
    return unit
