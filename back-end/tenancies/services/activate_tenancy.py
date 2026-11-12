from django.db import transaction
from rest_framework.exceptions import ValidationError

from tenancies.models import TenancyStatus
from tenancies.services.shared import notices
from tenancies.services.shared.transitions import (
    check_unit_is_free,
    current_tenants,
    lock_tenancy,
    require_status,
    save_status,
)

NO_TENANT = "Add a tenant first. Invite someone and wait for them to accept."


@transaction.atomic
def activate_tenancy(*, actor, tenancy_id, owned_by=None):
    tenancy = lock_tenancy(tenancy_id, owned_by)
    require_status(tenancy, {TenancyStatus.DRAFT})
    tenants = current_tenants(tenancy)
    if not tenants:
        raise ValidationError({"status": NO_TENANT})
    check_unit_is_free(tenancy)
    save_status(tenancy, TenancyStatus.ACTIVE, actor)
    notices.tenancy_started(tenancy, [party.tenant for party in tenants])
    return tenancy
