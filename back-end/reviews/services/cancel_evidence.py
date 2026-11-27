from django.db import transaction
from django.utils import timezone

from reviews.models import ReviewStatus
from reviews.services.shared.decisions import finish, require_open
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import find_evidence_I_wrote, reloaded


@transaction.atomic
def cancel_evidence(*, user, request_id):
    request = find_evidence_I_wrote(user, request_id, lock=True)
    require_open(request)
    came_from = request.status
    finish(request, ReviewStatus.CANCELLED, user, now=timezone.now())
    record_transition(
        request,
        ReviewStatus.CANCELLED,
        "CANCEL",
        user,
        "Withdrawn by the tenant",
        from_status=came_from,
    )
    return reloaded(request)
