from django.db import transaction
from django.utils import timezone

from properties.models import Property, PropertyOwner
from properties.services.get_property import get_property
from properties.services.shared.fields import blank_to_none
from properties.services.shared.landlords import find_landlord

FULL_OWNERSHIP = 100


@transaction.atomic
def create_property(*, actor, owner_id, fields):
    owner = find_landlord(owner_id)
    created = Property.objects.create(**blank_to_none(fields), created_by=actor)
    PropertyOwner.objects.create(
        property=created,
        owner=owner,
        is_primary_owner=True,
        ownership_percentage=FULL_OWNERSHIP,
        valid_from=timezone.now(),
        created_by=actor,
    )
    return get_property(property_id=created.pk)
