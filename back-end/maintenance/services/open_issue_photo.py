from django.core.files.storage import default_storage
from rest_framework.exceptions import NotFound

from maintenance.services.shared.scope import find_issue

NO_PHOTO = "No photo with this id on this issue."


def open_issue_photo(*, user, issue_id, file_id, as_admin=False):
    """Anyone who can see the issue; others get the issue's own 404."""
    issue = find_issue(user, issue_id, as_admin=as_admin)
    link = (
        issue.files.filter(file_id=file_id, file__deleted_at__isnull=True)
        .select_related("file")
        .first()
    )
    if link is None or not default_storage.exists(link.file.object_key):
        raise NotFound(NO_PHOTO)
    return link.file, default_storage.open(link.file.object_key, "rb")
