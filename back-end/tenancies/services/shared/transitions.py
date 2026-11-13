from datetime import timedelta

from rest_framework.exceptions import NotFound, ValidationError

from properties.models import OccupancyStatus
from tenancies.models import Tenancy, TenancyParty
from tenancies.services.shared.invitations import live_tenancies

UNIT_BUSY = "This unit already has an active tenancy in that period."


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


def sync_occupancy(unit, actor):
    if unit.occupancy_status == OccupancyStatus.UNAVAILABLE:
        return
    occupied = Tenancy.objects.active_on(unit).exists()
    occupancy = OccupancyStatus.OCCUPIED if occupied else OccupancyStatus.VACANT
    if unit.occupancy_status != occupancy:
        unit.occupancy_status = occupancy
        unit.updated_by = actor
        unit.row_version += 1
        unit.save()


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


def check_unit_is_free(tenancy):
    busy = (
        Tenancy.objects.active_on(tenancy.property_unit)
        .exclude(pk=tenancy.pk)
        .overlapping(tenancy.start_date, tenancy.end_date)
    )
    if busy.exists():
        raise ValidationError({"status": UNIT_BUSY})
