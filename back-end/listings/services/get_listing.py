from rest_framework.exceptions import NotFound

from listings.services.shared.queries import listed_properties, with_public_details


def get_listing(*, listing_id):
    found = with_public_details(listed_properties().filter(pk=listing_id)).first()
    if found is None:
        raise NotFound("This listing isn't available.")
    return found
