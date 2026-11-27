from django.db import transaction

from reviews.services.shared.correction_decisions import decide_correction
from reviews.services.shared.scope import find_correction_for_admin, reloaded_correction


@transaction.atomic
def reject_correction(*, admin, request_id, reason, idempotency_key):
    request = find_correction_for_admin(request_id, lock=True)
    decided = decide_correction(
        admin,
        request,
        approve=False,
        reason=reason.strip(),
        idempotency_key=idempotency_key,
    )
    return reloaded_correction(decided)
