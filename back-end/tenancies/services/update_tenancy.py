from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from properties.services.shared.rent import check_rent
from tenancies.models import TenancyStatus, TenancyTermChange, TermChangeStatus
from tenancies.services.shared import notices
from tenancies.services.shared.terms import (
    APPROVAL_WINDOW,
    MONEY_FIELDS,
    apply_money,
    close_open_changes,
    current_money,
    is_increase,
    record_applied_change,
)
from tenancies.services.shared.transitions import (
    check_unit_is_free,
    current_tenants,
    lock_tenancy,
    require_status,
)

EDITABLE_STATUSES = {TenancyStatus.DRAFT, TenancyStatus.PENDING, TenancyStatus.ACTIVE}
DATE_FIELDS = ("start_date", "end_date")
STARTED = "It has already started, so the start date can't change."
ENDS_IN_THE_PAST = "Choose a date in the future. To finish it now, use End tenancy."
ENDS_BEFORE_START = "End date must be after the start date."


@transaction.atomic
def update_tenancy(*, actor, tenancy_id, changes, owned_by=None):
    """Dates and notes apply at once. A rent or bond change applies at once too, unless the tenants
    would pay more: then it waits as a proposal until every current tenant approves it."""
    tenancy = lock_tenancy(tenancy_id, owned_by)
    require_status(tenancy, EDITABLE_STATUSES)
    clean = _clean(changes)
    now = timezone.now()
    before = current_money(tenancy)
    after = {field: clean.get(field, before[field]) for field in MONEY_FIELDS}
    dates_changed = [f for f in DATE_FIELDS if f in clean and clean[f] != getattr(tenancy, f)]
    for field, value in clean.items():
        if field not in MONEY_FIELDS:
            setattr(tenancy, field, value)
    _check_period(tenancy, dates_changed)
    check_rent(after["rent_amount"], after["rent_frequency"])
    if tenancy.status == TenancyStatus.ACTIVE and dates_changed:
        check_unit_is_free(tenancy)
    tenants = [party.tenant for party in current_tenants(tenancy)]
    outcome = (
        _handle_money(tenancy, before, after, actor, now, tenants) if after != before else None
    )
    tenancy.updated_by = actor
    tenancy.row_version += 1
    tenancy.save()
    if outcome == "proposed":
        notices.terms_proposed(tenancy, tenants)
    if dates_changed or outcome == "applied":
        notices.terms_changed(tenancy, tenants)
    return tenancy


def _handle_money(tenancy, before, after, actor, now, tenants):
    close_open_changes(tenancy, TermChangeStatus.SUPERSEDED, now)
    if tenants and is_increase(before, after):
        TenancyTermChange.objects.create(
            tenancy=tenancy,
            requires_approval=True,
            expires_at=now + APPROVAL_WINDOW,
            created_by=actor,
            **{f"from_{field}": value for field, value in before.items()},
            **after,
        )
        return "proposed"
    record_applied_change(tenancy, before, after, actor, now)
    apply_money(tenancy, after)
    return "applied"


def _clean(changes):
    clean = dict(changes)
    for field in ("notes", "rent_frequency"):
        if field in clean:
            clean[field] = clean[field] or None
    return clean


def _check_period(tenancy, dates_changed):
    if tenancy.status == TenancyStatus.ACTIVE and "start_date" in dates_changed:
        raise ValidationError({"start_date": STARTED})
    if tenancy.end_date is None:
        return
    if tenancy.end_date <= tenancy.start_date:
        raise ValidationError({"end_date": ENDS_BEFORE_START})
    if tenancy.status == TenancyStatus.ACTIVE and tenancy.end_date <= timezone.now().date():
        raise ValidationError({"end_date": ENDS_IN_THE_PAST})
