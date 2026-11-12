from django.db import transaction
from django.utils import timezone

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


@transaction.atomic
def cancel_tenancy(*, actor, tenancy_id, owned_by=None):
    tenancy = lock_tenancy(tenancy_id, owned_by)
    require_status(tenancy, {TenancyStatus.DRAFT, TenancyStatus.PENDING})
    tenants = current_tenants(tenancy)
    release_tenants(tenants, timezone.now().date(), actor)
    close_open_changes(tenancy, TermChangeStatus.CLOSED, timezone.now())
    save_status(tenancy, TenancyStatus.CANCELLED, actor)
    notices.tenancy_cancelled(tenancy, [party.tenant for party in tenants])
    return tenancy
