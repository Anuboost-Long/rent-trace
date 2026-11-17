from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound

from properties.models import Property, PropertyUnit
from properties.services.shared.errors import HasTenancies
from tenancies.models import Tenancy


@transaction.atomic
def delete_property(*, actor, property_id):
    target = Property.objects.select_for_update().filter(pk=property_id, deleted_at__isnull=True)
    target = target.first()
    if target is None:
        raise NotFound("No property with this id.")
    in_use = Tenancy.objects.filter(
        property_unit__property=target, deleted_at__isnull=True
    ).exists()
    if in_use:
        raise HasTenancies("This property has tenancies, so it can't be removed.")
    now = timezone.now()
    PropertyUnit.objects.filter(property=target, deleted_at__isnull=True).update(
        deleted_at=now, deleted_by=actor
    )
    target.deleted_at = now
    target.deleted_by = actor
    target.updated_by = actor
    target.row_version += 1
    target.save()
