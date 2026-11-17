from django.db import transaction
from django.utils import timezone

from tenancies.models import InvitationDecision
from tenancies.services.shared import notices
from tenancies.services.shared.decisions import open_request_for_decision, record_decision
from tenancies.services.shared.invitations import check_tenancy_is_open
from tenancies.services.shared.joining import join_tenancy
from tenancies.services.shared.transitions import lock_tenancy


@transaction.atomic
def approve_housemate(*, actor, tenancy_id, invitation_id, owned_by=None):
    """The landlord says yes. The person joins now if they already said yes too."""
    tenancy = lock_tenancy(tenancy_id, owned_by)
    check_tenancy_is_open(tenancy)
    now = timezone.now()
    invitation = open_request_for_decision(tenancy, invitation_id, now)
    record_decision(invitation, InvitationDecision.APPROVED, actor, now)
    notices.housemate_decided(invitation, tenancy, approved=True)
    if invitation.invitee_accepted_at is not None:
        join_tenancy(invitation, now, finished_by=actor)
    return invitation
