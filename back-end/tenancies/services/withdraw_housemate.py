from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound

from tenancies.services.request_housemate import lock_my_tenancy


@transaction.atomic
def withdraw_housemate(*, user, tenancy_id, invitation_id):
    """Only the tenant who asked can take their own request back."""
    tenancy = lock_my_tenancy(user, tenancy_id)
    invitation = (
        tenancy.invitations.outstanding()
        .select_for_update()
        .filter(pk=invitation_id, requested_by_tenant=True, created_by=user)
        .first()
    )
    if invitation is None:
        raise NotFound("No open request with this id.")
    invitation.revoked_at = timezone.now()
    invitation.updated_by = user
    invitation.row_version += 1
    invitation.save()
    return invitation
