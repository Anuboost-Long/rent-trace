from properties.services.shared.landlords import active_landlords

OWNER_OPTIONS_LIMIT = 500


def list_owner_options(*, q=None):
    landlords = active_landlords()
    if q:
        landlords = landlords.search(q)
    return list(landlords.order_by("first_name", "last_name", "id")[:OWNER_OPTIONS_LIMIT])
