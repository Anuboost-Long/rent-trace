from rest_framework.exceptions import ValidationError

from properties.services.shared.queries import current_owner_users

NO_OWNER = "This property has no current owner to act for."


def owner_acted_for(request, *, as_admin):
    """The primary owner a super admin acts for; None when the landlord acts themselves."""
    if not as_admin:
        return None
    place = request.target.condition_record.property_unit.property
    owners = current_owner_users(place)
    if not owners:
        raise ValidationError({"request": NO_OWNER})
    return owners[0]


def author_acted_for(request, *, as_admin):
    """The report's author a super admin acts for; None when the author acts themselves."""
    return request.requested_by if as_admin else None
