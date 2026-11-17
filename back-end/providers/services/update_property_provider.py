from django.db import transaction
from rest_framework.exceptions import NotFound

from providers.services.shared.property_links import find_owned_property, live_link, providers_on


@transaction.atomic
def update_property_provider(*, actor, property_id, provider_id, changes):
    property_ = find_owned_property(actor, property_id)
    link = live_link(property_, provider_id).select_for_update().first()
    if link is None:
        raise NotFound("This tradesperson is not linked to this property.")
    if "is_recommended" in changes:
        link.is_recommended = changes["is_recommended"]
    if "contract_notes" in changes:
        link.contract_notes = changes["contract_notes"] or None
    link.updated_by = actor
    link.row_version += 1
    link.save()
    return providers_on(actor, property_).get(pk=provider_id)
