from history.recording import changed_fields, record_business_change

OPTIONAL_TEXT = {
    "property_name",
    "address_line_2",
    "public_description",
    "private_notes",
    "unit_number",
    "description",
    "caption",
    "rent_frequency",
}


def blank_to_none(fields):
    return {k: (v or None) if k in OPTIONAL_TEXT else v for k, v in fields.items()}


def save_changes(actor, record, changes, *, action="UPDATE"):
    clean = blank_to_none(changes)
    before, after = changed_fields(record, clean)
    for field, value in clean.items():
        setattr(record, field, value)
    record.updated_by = actor
    record.row_version += 1
    record.save()
    record_business_change(record, actor, action, before, after, "Edited through the app")
