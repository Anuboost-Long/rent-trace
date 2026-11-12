from listings.services.shared.rent import weekly_rent

TYPE_NAMES = {
    "HOUSE": "House",
    "APARTMENT": "Apartment",
    "TOWNHOUSE": "Townhouse",
    "UNIT": "Unit",
    "STUDIO": "Studio",
    "ROOM": "Room",
    "OTHER": "Property",
}


def title_of(listing):
    return (
        listing.property_name
        or f"{TYPE_NAMES.get(listing.property_type, 'Property')} in {listing.suburb}"
    )


def listed_by(listing):
    """First name and last initial only: contact details stay private until a request is accepted."""
    if not listing.primary_owners:
        return None
    owner = listing.primary_owners[0].owner
    return f"{owner.first_name} {owner.last_name[:1]}."


def public_photos(listing):
    """Photos of the property itself and of its publicly shown units, covers first."""
    public_unit_ids = {unit.id for unit in listing.public_units}
    return [
        photo
        for photo in listing.photo_files
        if photo.property_unit_id is None or photo.property_unit_id in public_unit_ids
    ]


def unit_photos(listing, unit):
    return [photo for photo in listing.photo_files if photo.property_unit_id == unit.id]


def cover_of(listing):
    photos = public_photos(listing)
    own = [photo for photo in photos if photo.property_unit_id is None]
    return (own or photos or [None])[0]


def cheapest_unit(listing):
    priced = [unit for unit in listing.public_units if unit.rent_amount is not None]
    return min(
        priced, key=lambda unit: weekly_rent(unit.rent_amount, unit.rent_frequency), default=None
    )
