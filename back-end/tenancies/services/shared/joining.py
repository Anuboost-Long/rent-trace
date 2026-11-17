from rest_framework.exceptions import ValidationError

from accounts.security import tokens
from accounts.services.shared.account_rules import has_role, is_account_usable
from tenancies.models import Tenancy, TenancyInvitation, TenancyParty
from tenancies.services.shared import notices
from tenancies.services.shared.capacity import check_room
from tenancies.services.shared.errors import PrimaryTenantTaken
from tenancies.services.shared.invitations import INVALID_INVITATION, check_tenancy_is_open


def lock_pending_invitation(now, *, token=None, invitation_id=None):
    """Locks the tenancy first and the invitation second, the order every path that adds
    someone uses, so two people joining at once can't deadlock or pass the unit's limit."""
    pending = TenancyInvitation.objects.pending(now)
    if token is not None:
        found = pending.matching(tokens.digest(token)).first()
    else:
        found = pending.filter(pk=invitation_id).first()
    if found is None:
        return None
    Tenancy.objects.select_for_update().filter(pk=found.tenancy_id).first()
    return (
        pending.select_related("tenancy__property_unit__property")
        .select_for_update(of=("self",))
        .filter(pk=found.pk)
        .first()
    )


def join_tenancy(invitation, now, *, finished_by=None):
    """Both sides have said yes. The second yes can come days after the first, so everything is
    checked again here. The caller already holds the tenancy lock and the invitation lock."""
    tenancy = invitation.tenancy
    check_tenancy_is_open(tenancy)
    invitee = invitation.invitee_accepted_by
    if (
        invitation.revoked_at is not None
        or invitation.expires_at <= now
        or invitee is None
        or not is_account_usable(invitee, now)
        or not has_role(invitee, "TENANT")
    ):
        raise ValidationError({"invitation": INVALID_INVITATION})
    current = TenancyParty.objects.filter(tenancy=tenancy).current()
    if current.filter(tenant=invitee).exists():
        raise ValidationError({"invitation": "You are already a tenant here."})
    if invitation.is_primary and current.primary().exists():
        raise PrimaryTenantTaken()
    check_room(tenancy)
    invitation.accepted_at = now
    invitation.accepted_by = invitee
    invitation.updated_by = finished_by or invitee
    invitation.row_version += 1
    invitation.save()
    TenancyParty.objects.create(
        tenancy=tenancy,
        tenant=invitee,
        is_primary=invitation.is_primary,
        joined_at=now.date(),
        created_by=invitee,
    )
    notices.invitation_accepted(invitation, invitee, finished_by=finished_by)
