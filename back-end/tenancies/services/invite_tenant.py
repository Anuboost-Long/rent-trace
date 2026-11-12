from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from accounts.services.shared.account_rules import normalize_email
from accounts.services.shared.mail import send_after_commit
from tenancies.integrations import emails
from tenancies.models import TenancyInvitation, TenancyParty
from tenancies.services.shared import notices
from tenancies.services.shared.invitations import (
    check_tenancy_is_open,
    live_tenancies,
    new_link,
    place_name,
)


@transaction.atomic
def invite_tenant(*, actor, tenancy_id, fields, owned_by=None):
    tenancy = live_tenancies(owned_by).select_for_update().filter(pk=tenancy_id).first()
    if tenancy is None:
        raise NotFound("No tenancy with this id.")
    check_tenancy_is_open(tenancy)
    email = normalize_email(fields["email"])
    _check_can_invite(tenancy, email, fields["is_primary"])
    invitation = TenancyInvitation(
        tenancy=tenancy,
        email_normalized=email,
        is_primary=fields["is_primary"],
        created_by=actor,
    )
    raw = new_link(invitation, timezone.now())
    invitation.save()
    notices.invitation_sent(invitation, tenancy, actor, again=False)
    send_after_commit(emails.send_invitation, email, actor, place_name(tenancy), raw)
    return invitation


def _check_can_invite(tenancy, email, is_primary):
    if TenancyParty.objects.filter(tenancy=tenancy).current().with_tenant_email(email).exists():
        raise ValidationError({"email": "This person is already a tenant here."})
    if tenancy.invitations.outstanding().with_email(email).exists():
        raise ValidationError({"email": "This email already has an invitation. Resend it instead."})
    if is_primary and TenancyParty.objects.filter(tenancy=tenancy).current().primary().exists():
        raise ValidationError({"is_primary": "This tenancy already has a primary tenant."})
