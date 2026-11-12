from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from tenancies.models import TenancyTermChange, TermChangeStatus
from tenancies.services.shared.transitions import lock_tenancy


@transaction.atomic
def withdraw_term_change(*, actor, tenancy_id, change_id, owned_by=None):
    tenancy = lock_tenancy(tenancy_id, owned_by)
    change = (
        TenancyTermChange.objects.select_for_update(of=("self",))
        .filter(pk=change_id, tenancy=tenancy)
        .first()
    )
    if change is None:
        raise NotFound("No proposal with this id.")
    if change.status != TermChangeStatus.PENDING:
        raise ValidationError({"proposal": "This proposal is no longer open."})
    change.status = TermChangeStatus.WITHDRAWN
    change.decided_at = timezone.now()
    change.updated_by = actor
    change.row_version += 1
    change.save()
    return change
