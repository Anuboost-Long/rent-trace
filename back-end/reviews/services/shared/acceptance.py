from reviews.services.shared.history import record_change


def accept_version(request, actor, version, reason, *, on_behalf_of=None):
    """Makes the version the record's accepted one and writes the change history."""
    note = request.target.condition_record
    before = note.accepted_version.version_no if note.accepted_version else None
    record_change(
        request,
        actor,
        "ACCEPT_CONDITION_VERSION",
        {"accepted_version": before},
        {"accepted_version": version.version_no},
        reason,
        on_behalf_of=on_behalf_of,
    )
    note.accepted_version = version
    note.updated_by = actor
    note.row_version += 1
    note.save()
