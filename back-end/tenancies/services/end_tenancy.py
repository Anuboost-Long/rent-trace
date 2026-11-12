from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from tenancies.models import TenancyStatus, TermChangeStatus
from tenancies.services.shared import notices
from tenancies.services.shared.terms import close_open_changes
from tenancies.services.shared.transitions import (
    current_tenants,
    lock_tenancy,
    release_tenants,
    require_status,
    save_status,
)

NOT_STARTED = "This tenancy hasn't started yet. Cancel it instead."


@transaction.atomic
def end_tenancy(*, actor, tenancy_id, owned_by=None):
    tenancy = lock_tenancy(tenancy_id, owned_by)
    require_status(tenancy, {TenancyStatus.ACTIVE})
    today = timezone.now().date()
    if today <= tenancy.start_date:
        raise ValidationError({"status": NOT_STARTED})
    if tenancy.end_date is None or tenancy.end_date > today:
        tenancy.end_date = today
    tenants = current_tenants(tenancy)
    release_tenants(tenants, today, actor)
    close_open_changes(tenancy, TermChangeStatus.CLOSED, timezone.now())
    save_status(tenancy, TenancyStatus.ENDED, actor)
    notices.tenancy_ended(tenancy, [party.tenant for party in tenants])
    return tenancy
