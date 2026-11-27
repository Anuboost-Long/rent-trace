from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from maintenance.models import MaintenanceStatus
from maintenance.services.shared.scope import find_issue

NO_PHOTO = "No photo with this id on this issue."
CLOSED = "This issue is closed, so photos can no longer be removed."


@transaction.atomic
def remove_issue_photo(*, user, issue_id, file_id):
    issue = find_issue(user, issue_id, lock=True)
    link = (
        issue.files.filter(file_id=file_id, file__deleted_at__isnull=True)
        .select_related("file")
        .first()
    )
    if link is None or link.file.uploaded_by_id != user.pk:
        raise NotFound(NO_PHOTO)
    if issue.status == MaintenanceStatus.CLOSED:
        raise ValidationError({"issue": CLOSED})
    stored = link.file
    stored.deleted_at = timezone.now()
    stored.deleted_by = user
    stored.updated_by = user
    stored.row_version += 1
    stored.save()
    return issue.pk
