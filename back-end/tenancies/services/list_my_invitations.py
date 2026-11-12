from django.utils import timezone

from tenancies.models import TenancyInvitation


def list_my_invitations(*, user):
    return (
        TenancyInvitation.objects.pending(timezone.now())
        .with_email(user.email_normalized)
        .select_related("tenancy__property_unit__property", "created_by")
        .order_by("-id")
    )
