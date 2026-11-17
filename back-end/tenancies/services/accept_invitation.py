from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from tenancies.models import InvitationDecision
from tenancies.services.shared.invitations import CLOSED_STATUSES, INVALID_INVITATION
from tenancies.services.shared.joining import join_tenancy, lock_pending_invitation


@transaction.atomic
def accept_invitation(*, user, token=None, invitation_id=None):
    """The invited person says yes. They join now if the landlord already agreed; otherwise they
    wait for the landlord. A landlord's own invitation counts as the landlord's yes."""
    now = timezone.now()
    invitation = lock_pending_invitation(now, token=token, invitation_id=invitation_id)
    if not _is_addressed_to(invitation, user) or invitation.tenancy.status in CLOSED_STATUSES:
        raise ValidationError({"invitation": INVALID_INVITATION})
    if invitation.invitee_accepted_at is None:
        invitation.invitee_accepted_at = now
        invitation.invitee_accepted_by = user
        invitation.updated_by = user
        invitation.row_version += 1
        invitation.save()
    if invitation.landlord_decision == InvitationDecision.APPROVED:
        join_tenancy(invitation, now)
    return invitation


def _is_addressed_to(invitation, user):
    return (
        invitation is not None
        and user.email_verified_at is not None
        and user.email_normalized == invitation.email_normalized
    )
