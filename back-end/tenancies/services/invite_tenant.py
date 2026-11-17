from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound

from accounts.services.shared.account_rules import normalize_email
from accounts.services.shared.mail import send_after_commit
from tenancies.integrations import emails
from tenancies.models import InvitationDecision, TenancyInvitation
from tenancies.services.shared import notices
from tenancies.services.shared.capacity import check_room
from tenancies.services.shared.checks import check_can_invite
from tenancies.services.shared.invitations import (
    check_tenancy_is_open,
    live_tenancies,
    new_link,
    place_name,
)


@transaction.atomic
def invite_tenant(*, actor, tenancy_id, fields, owned_by=None):
    tenancy = (
        live_tenancies(owned_by)
        .select_related("property_unit__property")
        .select_for_update(of=("self",))
        .filter(pk=tenancy_id)
        .first()
    )
    if tenancy is None:
        raise NotFound("No tenancy with this id.")
    check_tenancy_is_open(tenancy)
    email = normalize_email(fields["email"])
    check_can_invite(tenancy, email, fields["is_primary"])
    check_room(tenancy)
    now = timezone.now()
    invitation = TenancyInvitation(
        tenancy=tenancy,
        email_normalized=email,
        is_primary=fields["is_primary"],
        created_by=actor,
        landlord_decision=InvitationDecision.APPROVED,
        landlord_decided_at=now,
        landlord_decided_by=actor,
    )
    raw = new_link(invitation, now)
    invitation.save()
    notices.invitation_sent(invitation, tenancy, actor, again=False)
    send_after_commit(emails.send_invitation, email, actor, place_name(tenancy), raw)
    return invitation
