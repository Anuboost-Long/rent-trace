from providers.services.shared.property_links import find_owned_property, providers_on


def list_property_providers(*, owner, property_id):
    return providers_on(owner, find_owned_property(owner, property_id))
