from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from maintenance.services.shared.rules import require_landlord, require_open
from maintenance.services.shared.scope import find_issue

NO_VISIT = "Book a tradesperson before marking the visit done."
ALREADY_DONE = "This visit is already marked done."


@transaction.atomic
def complete_visit(*, user, issue_id):
    issue = find_issue(user, issue_id, lock=True)
    require_landlord(issue, user)
    require_open(issue)
    current = issue.assignments.filter(superseded_by__isnull=True).first()
    if current is None:
        raise ValidationError({"assignment": NO_VISIT})
    if current.completed_at is not None:
        raise ValidationError({"assignment": ALREADY_DONE})
    current.completed_at = timezone.now()
    current.save(update_fields=["completed_at"])
    return current
