from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from reviews.models import ReviewStatus
from reviews.services.shared.decisions import finish
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import find_removal_I_asked, reloaded_removal

NOT_WAITING = "This removal request has already been decided or withdrawn."


@transaction.atomic
def cancel_removal(*, user, request_id):
    request = find_removal_I_asked(user, request_id, lock=True)
    if request.status != ReviewStatus.PENDING_REVIEW:
        raise ValidationError({"request": NOT_WAITING})
    finish(request, ReviewStatus.CANCELLED, user, now=timezone.now())
    record_transition(
        request,
        ReviewStatus.CANCELLED,
        "CANCEL",
        user,
        "Withdrawn by the person who asked",
        from_status=ReviewStatus.PENDING_REVIEW,
    )
    return reloaded_removal(request)
