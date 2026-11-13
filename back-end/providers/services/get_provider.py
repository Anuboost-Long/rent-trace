from rest_framework.exceptions import NotFound

from providers.models import ServiceProvider


def get_provider(*, owner, provider_id):
    found = (
        ServiceProvider.objects.live()
        .owned_by(owner)
        .with_links_and_categories()
        .filter(pk=provider_id)
        .first()
    )
    if found is None:
        raise NotFound("No provider with this id.")
    return found
