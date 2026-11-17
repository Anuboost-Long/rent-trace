from django.utils import timezone
from rest_framework.exceptions import NotFound

from accounts.security import tokens
from tenancies.models import TenancyInvitation

INVALID_INVITATION = "This invitation is invalid or has expired."


def preview_invitation(*, token):
    invitation = (
        TenancyInvitation.objects.pending(timezone.now())
        .matching(tokens.digest(token))
        .select_related("tenancy__property_unit__property", "created_by")
        .first()
    )
    if invitation is None:
        raise NotFound(INVALID_INVITATION)
    return invitation
