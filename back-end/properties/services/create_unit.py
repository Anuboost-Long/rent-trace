from rest_framework.exceptions import NotFound

from properties.models import PropertyUnit
from properties.services.shared.fields import blank_to_none
from properties.services.shared.queries import live_properties


def create_unit(*, actor, property_id, fields, owned_by=None):
    target = live_properties(owned_by).filter(pk=property_id).first()
    if target is None:
        raise NotFound("No property with this id.")
    return PropertyUnit.objects.create(property=target, **blank_to_none(fields), created_by=actor)
