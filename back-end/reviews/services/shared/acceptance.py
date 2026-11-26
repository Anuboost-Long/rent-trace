from reviews.services.shared.history import record_change


def accept_version(request, actor, version, reason):
    """Makes the version the record's accepted one and writes the change history."""
    note = request.target.condition_record
    record_change(
        request,
        actor,
        "ACCEPT_CONDITION_VERSION",
        {"accepted_version": None},
        {"accepted_version": version.version_no},
        reason,
    )
    note.accepted_version = version
    note.updated_by = actor
    note.row_version += 1
    note.save()
