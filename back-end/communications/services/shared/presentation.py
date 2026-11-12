from listings.services.shared.presentation import title_of


def listing_title(contact_request):
    return title_of(contact_request.property)


def primary_owner(contact_request):
    owners = contact_request.property.primary_owners
    return owners[0].owner if owners else None
