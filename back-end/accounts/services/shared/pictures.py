def hide_file(stored, actor, now):
    """Soft delete: the file row and its bytes stay, but nothing serves it any more."""
    stored.deleted_at = now
    stored.deleted_by = actor
    stored.updated_by = actor
    stored.row_version += 1
    stored.save()
