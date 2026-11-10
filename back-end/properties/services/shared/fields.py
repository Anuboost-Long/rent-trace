OPTIONAL_TEXT = {
    "property_name",
    "address_line_2",
    "public_description",
    "private_notes",
    "unit_number",
    "description",
    "caption",
}


def blank_to_none(fields):
    return {k: (v or None) if k in OPTIONAL_TEXT else v for k, v in fields.items()}


def save_changes(actor, record, changes):
    for field, value in blank_to_none(changes).items():
        setattr(record, field, value)
    record.updated_by = actor
    record.row_version += 1
    record.save()
