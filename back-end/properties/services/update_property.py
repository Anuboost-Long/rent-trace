from django.db import transaction
from rest_framework.exceptions import NotFound

from properties.services.get_property import get_property
from properties.services.shared.fields import save_changes
from properties.services.shared.queries import live_properties


@transaction.atomic
def update_property(*, actor, property_id, changes, owned_by=None):
    target = live_properties(owned_by).select_for_update().filter(pk=property_id).first()
    if target is None:
        raise NotFound("No property with this id.")
    save_changes(actor, target, changes)
    return get_property(property_id=property_id, owned_by=owned_by)
