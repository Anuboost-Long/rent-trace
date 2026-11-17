from rest_framework.exceptions import NotFound

from properties.services.shared.queries import live_properties, with_owners_and_units


def get_property(*, property_id, owned_by=None):
    found = with_owners_and_units(live_properties(owned_by).filter(pk=property_id)).first()
    if found is None:
        raise NotFound("No property with this id.")
    return found
