from datetime import timedelta

from rest_framework.exceptions import ValidationError

from accounts.security import tokens
from properties.services.shared.queries import live_properties
from tenancies.models import Tenancy, TenancyStatus

INVITATION_LIFETIME = timedelta(days=7)
INVALID_INVITATION = "This invitation is invalid or has expired."
CLOSED_STATUSES = {TenancyStatus.ENDED, TenancyStatus.CANCELLED}


def invitation_status(invitation, now):
    if invitation.accepted_at:
        return "ACCEPTED"
    if invitation.revoked_at:
        return "REVOKED"
    return "EXPIRED" if invitation.expires_at <= now else "PENDING"


def new_link(invitation, now):
    raw = tokens.new_secret()
    invitation.token_hash = tokens.digest(raw)
    invitation.expires_at = now + INVITATION_LIFETIME
    return raw


def live_tenancies(owned_by=None):
    return Tenancy.objects.live().in_properties(live_properties(owned_by))


def check_tenancy_is_open(tenancy):
    if tenancy.status in CLOSED_STATUSES:
        raise ValidationError({"tenancy": "This tenancy has ended or been cancelled."})


def place_name(tenancy):
    place = tenancy.property_unit.property
    return place.property_name or f"{place.address_line_1}, {place.suburb}"
