from datetime import timedelta

from tenancies.models import TenancyTermChange, TermChangeStatus, TermDecision

APPROVAL_WINDOW = timedelta(days=14)
MONEY_FIELDS = ("rent_amount", "rent_frequency", "bond_amount")
PERIODS_PER_YEAR = {"WEEKLY": 52, "FORTNIGHTLY": 26, "MONTHLY": 12}


def current_money(tenancy):
    return {field: getattr(tenancy, field) for field in MONEY_FIELDS}


def yearly_rent(amount, frequency):
    """What a year of rent adds up to. Comparing yearly totals is exact, with no rounding."""
    return amount * PERIODS_PER_YEAR[frequency] if amount is not None else 0


def is_increase(before, after):
    rent_rises = yearly_rent(after["rent_amount"], after["rent_frequency"]) > yearly_rent(
        before["rent_amount"], before["rent_frequency"]
    )
    return rent_rises or (after["bond_amount"] or 0) > (before["bond_amount"] or 0)


def close_open_changes(tenancy, status, now):
    TenancyTermChange.objects.filter(tenancy=tenancy).pending().update(
        status=status, decided_at=now
    )


def record_applied_change(tenancy, before, after, actor, now):
    """Every money change leaves a row, so the table is the history of rent and bond."""
    return TenancyTermChange.objects.create(
        tenancy=tenancy,
        status=TermChangeStatus.APPLIED,
        requires_approval=False,
        decided_at=now,
        created_by=actor,
        **{f"from_{field}": value for field, value in before.items()},
        **after,
    )


def apply_money(tenancy, money):
    for field, value in money.items():
        setattr(tenancy, field, value)


def change_money(change):
    return {field: getattr(change, field) for field in MONEY_FIELDS}


def everyone_approved(change, tenants):
    approved = set(
        change.decisions.filter(decision=TermDecision.APPROVED).values_list("tenant_id", flat=True)
    )
    return all(tenant.pk in approved for tenant in tenants)
