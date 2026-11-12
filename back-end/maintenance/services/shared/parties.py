from common.models import PartySide
from properties.models import PropertyOwner
from tenancies.models import TenancyParty


def current_owner_users(issue):
    owners = PropertyOwner.objects.filter(
        property=issue.property_unit.property_id, valid_to__isnull=True, deleted_at__isnull=True
    ).select_related("owner")
    return [row.owner for row in owners]


def current_tenant_users(issue):
    if issue.tenancy_id is None:
        return []
    parties = TenancyParty.objects.filter(tenancy_id=issue.tenancy_id).current()
    return [party.tenant for party in parties.select_related("tenant")]


def side_of(user, issue):
    """Which side the person acts for on this issue today, or None if they only get to read it."""
    if any(owner.pk == user.pk for owner in current_owner_users(issue)):
        return PartySide.LANDLORD
    if any(tenant.pk == user.pk for tenant in current_tenant_users(issue)):
        return PartySide.TENANT
    return None


def other_side_users(issue, side):
    return current_tenant_users(issue) if side == PartySide.LANDLORD else current_owner_users(issue)
