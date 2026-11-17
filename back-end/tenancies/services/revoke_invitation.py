from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound

from tenancies.services.shared.invitations import live_tenancies


@transaction.atomic
def revoke_invitation(*, actor, tenancy_id, invitation_id, owned_by=None):
    tenancy = live_tenancies(owned_by).select_for_update().filter(pk=tenancy_id).first()
    if tenancy is None:
        raise NotFound("No tenancy with this id.")
    invitation = tenancy.invitations.outstanding().filter(pk=invitation_id).first()
    if invitation is None:
        raise NotFound("No open invitation with this id.")
    invitation.revoked_at = timezone.now()
    invitation.updated_by = actor
    invitation.row_version += 1
    invitation.save()
    return invitation
