from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from accounts.services.shared.mail import send_after_commit
from tenancies.integrations import emails
from tenancies.services.shared import notices
from tenancies.services.shared.invitations import (
    check_tenancy_is_open,
    live_tenancies,
    new_link,
    place_name,
)

ALREADY_ACCEPTED = "They already accepted, so there is nothing to send again."


@transaction.atomic
def resend_invitation(*, actor, tenancy_id, invitation_id, owned_by=None):
    tenancy = live_tenancies(owned_by).select_for_update().filter(pk=tenancy_id).first()
    if tenancy is None:
        raise NotFound("No tenancy with this id.")
    check_tenancy_is_open(tenancy)
    invitation = tenancy.invitations.outstanding().filter(pk=invitation_id).first()
    if invitation is None:
        raise NotFound("No open invitation with this id.")
    if invitation.invitee_accepted_at is not None:
        raise ValidationError({"invitation": ALREADY_ACCEPTED})
    needs_landlord = invitation.requested_by_tenant and invitation.landlord_decision is None
    raw = new_link(invitation, timezone.now())
    invitation.updated_by = actor
    invitation.row_version += 1
    invitation.save()
    notices.invitation_sent(invitation, tenancy, actor, again=True, needs_landlord=needs_landlord)
    send_after_commit(
        emails.send_invitation,
        invitation.email_normalized,
        actor,
        place_name(tenancy),
        raw,
        needs_landlord,
    )
    return invitation
