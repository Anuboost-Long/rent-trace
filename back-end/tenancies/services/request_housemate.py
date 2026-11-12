from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from accounts.services.shared.account_rules import normalize_email
from accounts.services.shared.mail import send_after_commit
from properties.services.shared.queries import current_owner_users
from tenancies.integrations import emails
from tenancies.models import Tenancy, TenancyInvitation, TenancyParty
from tenancies.services.shared import notices
from tenancies.services.shared.capacity import check_room
from tenancies.services.shared.checks import check_can_invite
from tenancies.services.shared.invitations import check_tenancy_is_open, new_link, place_name

MAX_OPEN_REQUESTS = 5
MAX_REQUESTS_PER_DAY = 10
OWN_EMAIL = "That's your own email address."
TOO_MANY_OPEN = "This tenancy already has 5 requests waiting. Wait for answers or withdraw one."
TOO_MANY_TODAY = "You've sent a lot of requests today. Try again tomorrow."


def lock_my_tenancy(user, tenancy_id):
    """404 unless the person is a current tenant of it; locks the tenancy for the change."""
    is_member = TenancyParty.objects.filter(tenancy_id=tenancy_id, tenant=user).current().exists()
    found = (
        Tenancy.objects.live()
        .select_related("property_unit__property")
        .select_for_update(of=("self",))
        .filter(pk=tenancy_id)
        .first()
        if is_member
        else None
    )
    if found is None:
        raise NotFound("No tenancy with this id.")
    return found


@transaction.atomic
def request_housemate(*, user, tenancy_id, email):
    tenancy = lock_my_tenancy(user, tenancy_id)
    check_tenancy_is_open(tenancy)
    now = timezone.now()
    address = normalize_email(email)
    if address == user.email_normalized:
        raise ValidationError({"email": OWN_EMAIL})
    check_can_invite(tenancy, address, False)
    check_room(tenancy)
    _check_limits(tenancy, user, now)
    invitation = TenancyInvitation(
        tenancy=tenancy, email_normalized=address, created_by=user, requested_by_tenant=True
    )
    raw = new_link(invitation, now)
    invitation.save()
    notices.housemate_requested(tenancy, user)
    notices.invitation_sent(invitation, tenancy, user, again=False, needs_landlord=True)
    place = place_name(tenancy)
    send_after_commit(emails.send_invitation, address, user, place, raw, True)
    owners = current_owner_users(tenancy.property_unit.property)
    if owners:
        send_after_commit(emails.send_housemate_request, owners[0], user, place)
    return invitation


def _check_limits(tenancy, user, now):
    open_requests = tenancy.invitations.outstanding().filter(requested_by_tenant=True)
    if open_requests.count() >= MAX_OPEN_REQUESTS:
        raise ValidationError({"email": TOO_MANY_OPEN})
    today = TenancyInvitation.objects.filter(
        created_by=user, requested_by_tenant=True, created_at__gte=now - timedelta(days=1)
    )
    if today.count() >= MAX_REQUESTS_PER_DAY:
        raise ValidationError({"email": TOO_MANY_TODAY})
