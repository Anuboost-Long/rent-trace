from django.db import transaction
from django.utils import timezone

from tenancies.models import InvitationDecision
from tenancies.services.shared import notices
from tenancies.services.shared.decisions import open_request_for_decision, record_decision
from tenancies.services.shared.invitations import check_tenancy_is_open
from tenancies.services.shared.transitions import lock_tenancy


@transaction.atomic
def decline_housemate(*, actor, tenancy_id, invitation_id, owned_by=None):
    tenancy = lock_tenancy(tenancy_id, owned_by)
    check_tenancy_is_open(tenancy)
    now = timezone.now()
    invitation = open_request_for_decision(tenancy, invitation_id, now)
    record_decision(invitation, InvitationDecision.DECLINED, actor, now)
    notices.housemate_decided(invitation, tenancy, approved=False)
    return invitation
