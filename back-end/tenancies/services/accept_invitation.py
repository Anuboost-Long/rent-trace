from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.security import tokens
from tenancies.models import TenancyInvitation, TenancyParty
from tenancies.services.shared import notices
from tenancies.services.shared.errors import PrimaryTenantTaken
from tenancies.services.shared.invitations import CLOSED_STATUSES, INVALID_INVITATION


@transaction.atomic
def accept_invitation(*, user, token=None, invitation_id=None):
    now = timezone.now()
    invitation = _find_pending(now, token, invitation_id)
    if not _is_addressed_to(invitation, user) or invitation.tenancy.status in CLOSED_STATUSES:
        raise ValidationError({"invitation": INVALID_INVITATION})
    _check_can_join(invitation.tenancy, user, invitation.is_primary)
    invitation.accepted_at = now
    invitation.accepted_by = user
    invitation.updated_by = user
    invitation.row_version += 1
    invitation.save()
    TenancyParty.objects.create(
        tenancy=invitation.tenancy,
        tenant=user,
        is_primary=invitation.is_primary,
        joined_at=now.date(),
        created_by=user,
    )
    notices.invitation_accepted(invitation, user)
    return invitation


def _find_pending(now, token, invitation_id):
    pending = (
        TenancyInvitation.objects.pending(now)
        .select_related("tenancy")
        .select_for_update(of=("self",))
    )
    if token is not None:
        return pending.matching(tokens.digest(token)).first()
    return pending.filter(pk=invitation_id).first()


def _is_addressed_to(invitation, user):
    return (
        invitation is not None
        and user.email_verified_at is not None
        and user.email_normalized == invitation.email_normalized
    )


def _check_can_join(tenancy, user, is_primary):
    current = TenancyParty.objects.filter(tenancy=tenancy).current()
    if current.filter(tenant=user).exists():
        raise ValidationError({"invitation": "You are already a tenant here."})
    if is_primary and current.primary().exists():
        raise PrimaryTenantTaken()
