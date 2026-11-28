import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from history.recording import record_business_change
from tenancies.models import TenancyTermChange, TenancyTermDecision, TermChangeStatus, TermDecision
from tenancies.services.request_housemate import lock_my_tenancy
from tenancies.services.shared import notices
from tenancies.services.shared.invitations import check_tenancy_is_open
from tenancies.services.shared.terms import (
    apply_money,
    change_money,
    current_money,
    everyone_approved,
)
from tenancies.services.shared.transitions import current_tenants

NO_LONGER_OPEN = "This proposal is no longer open."
EXPIRED = "This proposal has expired. Ask your landlord to send it again."
ALREADY_ANSWERED = "You've already answered this proposal."
MONEY_MOVED = (
    "The rent or bond has changed since this was proposed. Ask your landlord to send it again."
)


@transaction.atomic
def respond_to_term_change(*, user, tenancy_id, change_id, decision):
    """A tenant approves or declines one specific proposal. It applies once every current tenant has
    approved; one decline ends it. Locks the tenancy first, then the proposal."""
    tenancy = lock_my_tenancy(user, tenancy_id)
    check_tenancy_is_open(tenancy)
    now = timezone.now()
    change = _lock_change(tenancy, change_id)
    _check_still_open(change, now)
    earlier = change.decisions.filter(tenant=user).first()
    if earlier is not None:
        if earlier.decision == decision:
            return change
        raise ValidationError({"decision": ALREADY_ANSWERED})
    TenancyTermDecision.objects.create(
        change=change, tenant=user, decision=decision, created_by=user, correlation_id=uuid.uuid4()
    )
    if decision == TermDecision.DECLINED:
        _finish(change, TermChangeStatus.DECLINED, user, now)
        notices.terms_declined(tenancy, change.created_by, user)
        return change
    if current_money(tenancy) != _from_money(change):
        raise ValidationError({"proposal": MONEY_MOVED})
    tenants = [party.tenant for party in current_tenants(tenancy)]
    if everyone_approved(change, tenants):
        _apply(tenancy, change, user, now)
        notices.terms_applied(tenancy, change.created_by, tenants)
    return change


def _lock_change(tenancy, change_id):
    found = (
        TenancyTermChange.objects.select_for_update(of=("self",))
        .select_related("created_by")
        .filter(pk=change_id, tenancy=tenancy)
        .first()
    )
    if found is None:
        raise NotFound("No proposal with this id.")
    return found


def _check_still_open(change, now):
    if change.status != TermChangeStatus.PENDING:
        raise ValidationError({"proposal": NO_LONGER_OPEN})
    if change.expires_at <= now:
        raise ValidationError({"proposal": EXPIRED})


def _from_money(change):
    return {
        "rent_amount": change.from_rent_amount,
        "rent_frequency": change.from_rent_frequency,
        "bond_amount": change.from_bond_amount,
    }


def _finish(change, status, actor, now):
    change.status = status
    change.decided_at = now
    change.updated_by = actor
    change.row_version += 1
    change.save()


def _apply(tenancy, change, approver, now):
    before, after = current_money(tenancy), change_money(change)
    apply_money(tenancy, after)
    tenancy.updated_by = approver
    tenancy.row_version += 1
    tenancy.save()
    moved = [field for field in after if before[field] != after[field]]
    record_business_change(
        tenancy,
        approver,
        "APPLY_TERM_CHANGE",
        {field: before[field] for field in moved},
        {field: after[field] for field in moved},
        "Approved by every current tenant",
    )
    _finish(change, TermChangeStatus.APPLIED, approver, now)
