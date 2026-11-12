from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from properties.services.shared.rent import check_rent
from tenancies.models import TenancyStatus
from tenancies.services.shared import notices
from tenancies.services.shared.transitions import (
    check_unit_is_free,
    current_tenants,
    lock_tenancy,
    require_status,
)

EDITABLE_STATUSES = {TenancyStatus.DRAFT, TenancyStatus.PENDING, TenancyStatus.ACTIVE}
TENANT_VISIBLE = ("start_date", "end_date", "rent_amount", "rent_frequency", "bond_amount")
STARTED = "It has already started, so the start date can't change."
ENDS_IN_THE_PAST = "Choose a date in the future. To finish it now, use End tenancy."
ENDS_BEFORE_START = "End date must be after the start date."


@transaction.atomic
def update_tenancy(*, actor, tenancy_id, changes, owned_by=None):
    tenancy = lock_tenancy(tenancy_id, owned_by)
    require_status(tenancy, EDITABLE_STATUSES)
    clean = _clean(changes)
    changed = [
        field
        for field in TENANT_VISIBLE
        if field in clean and clean[field] != getattr(tenancy, field)
    ]
    for field, value in clean.items():
        setattr(tenancy, field, value)
    _check_period(tenancy, changed)
    check_rent(tenancy.rent_amount, tenancy.rent_frequency)
    if tenancy.status == TenancyStatus.ACTIVE and {"start_date", "end_date"} & set(changed):
        check_unit_is_free(tenancy)
    tenancy.updated_by = actor
    tenancy.row_version += 1
    tenancy.save()
    if changed:
        tenants = [party.tenant for party in current_tenants(tenancy)]
        notices.terms_changed(tenancy, tenants)
    return tenancy


def _clean(changes):
    clean = dict(changes)
    for field in ("notes", "rent_frequency"):
        if field in clean:
            clean[field] = clean[field] or None
    return clean


def _check_period(tenancy, changed):
    if tenancy.status == TenancyStatus.ACTIVE and "start_date" in changed:
        raise ValidationError({"start_date": STARTED})
    if tenancy.end_date is None:
        return
    if tenancy.end_date <= tenancy.start_date:
        raise ValidationError({"end_date": ENDS_BEFORE_START})
    if tenancy.status == TenancyStatus.ACTIVE and tenancy.end_date <= timezone.now().date():
        raise ValidationError({"end_date": ENDS_IN_THE_PAST})
