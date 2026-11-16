from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound

from providers.services.shared.property_links import find_owned_property, live_link
from providers.services.shared.provider_links import soft_delete


@transaction.atomic
def unlink_provider(*, actor, property_id, provider_id):
    property_ = find_owned_property(actor, property_id)
    link = live_link(property_, provider_id).select_for_update().first()
    if link is None:
        raise NotFound("This tradesperson is not linked to this property.")
    soft_delete(link, actor, timezone.now())
