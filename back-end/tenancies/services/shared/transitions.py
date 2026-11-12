from datetime import timedelta

from rest_framework.exceptions import NotFound, ValidationError

from tenancies.models import TenancyParty
from tenancies.services.shared.invitations import live_tenancies


def lock_tenancy(tenancy_id, owned_by):
    found = (
        live_tenancies(owned_by)
        .select_related("property_unit__property")
        .select_for_update(of=("self",))
        .filter(pk=tenancy_id)
        .first()
    )
    if found is None:
        raise NotFound("No tenancy with this id.")
    return found


def require_status(tenancy, allowed):
    if tenancy.status not in allowed:
        raise ValidationError(
            {"status": f"This tenancy is {tenancy.status.lower()}, so it can't be changed."}
        )


def save_status(tenancy, status, actor):
    tenancy.status = status
    tenancy.updated_by = actor
    tenancy.row_version += 1
    tenancy.save()


def current_tenants(tenancy):
    parties = TenancyParty.objects.filter(tenancy=tenancy).current().select_related("tenant")
    return list(parties.order_by("id"))


def release_tenants(parties, today, actor):
    """A tenant can only leave after the day they joined, so someone who joined today leaves tomorrow."""
    for party in parties:
        party.left_at = max(today, party.joined_at + timedelta(days=1))
        party.updated_by = actor
        party.row_version += 1
        party.save()
