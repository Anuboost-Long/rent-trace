from django.db import transaction

from reviews.services.shared.cases import decide_case, find_admin_case


@transaction.atomic
def reject_dispute(*, admin, case_id, reason, idempotency_key):
    case = find_admin_case(case_id, lock=True)
    return decide_case(
        admin, case, approve=False, reason=reason.strip(), idempotency_key=idempotency_key
    )
