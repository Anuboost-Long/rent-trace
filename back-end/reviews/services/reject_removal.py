from django.db import transaction

from reviews.services.shared.removal_decisions import decide_removal
from reviews.services.shared.scope import find_removal_for_admin, reloaded_removal


@transaction.atomic
def reject_removal(*, admin, request_id, reason, idempotency_key):
    request = find_removal_for_admin(request_id, lock=True)
    decided = decide_removal(
        admin,
        request,
        approve=False,
        reason=reason.strip(),
        idempotency_key=idempotency_key,
    )
    return reloaded_removal(decided)
