from conditions.services.shared.scope import find_owned_unit, unit_notes


def list_conditions(*, landlord, unit_id):
    find_owned_unit(landlord, unit_id)
    return unit_notes(unit_id).order_by("id")
