from rest_framework.exceptions import NotFound

from tenancies.models import InvitationDecision


def open_request_for_decision(tenancy, invitation_id, now):
    found = (
        tenancy.invitations.pending(now)
        .select_for_update()
        .filter(pk=invitation_id, requested_by_tenant=True, landlord_decision__isnull=True)
        .first()
    )
    if found is None:
        raise NotFound("No tenant request waiting for a decision with this id.")
    return found


def record_decision(invitation, decision, actor, now):
    invitation.landlord_decision = decision
    invitation.landlord_decided_at = now
    invitation.landlord_decided_by = actor
    if decision == InvitationDecision.DECLINED:
        invitation.revoked_at = now
    invitation.updated_by = actor
    invitation.row_version += 1
    invitation.save()
