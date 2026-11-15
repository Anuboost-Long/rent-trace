from datetime import timedelta

from django.utils import timezone

from accounts.models import AccountAccessHistory, AccountStatus, Ban, User
from accounts.services.shared.permissions import granted_codes
from properties.models import PropertyUnit
from properties.services.shared.queries import live_properties
from tenancies.models import Tenancy, TenancyInvitation, TenancyStatus

ENDING_SOON_DAYS = 60
RECENT_ACTIVITY_COUNT = 6


def get_overview(*, user):
    allowed = granted_codes(user)
    now = timezone.now()
    return {
        "people": _people() if "accounts.view" in allowed else None,
        "properties": _properties() if "properties.admin_view" in allowed else None,
        "tenancies": _tenancies(now) if "tenancies.admin_view" in allowed else None,
        "active_bans": Ban.objects.active(now).count() if "bans.view" in allowed else None,
        "activity": _recent_activity() if "accounts.view" in allowed else None,
    }


def get_landlord_overview(*, user):
    allowed = granted_codes(user)
    now = timezone.now()
    return {
        "people": None,
        "properties": _properties(user) if "properties.view" in allowed else None,
        "tenancies": _tenancies(now, user) if "tenancies.view" in allowed else None,
        "active_bans": None,
        "activity": None,
    }


def _people():
    users = User.objects.not_deleted()
    return {
        "users": users.count(),
        "suspended": users.filter(account_status=AccountStatus.SUSPENDED).count(),
    }


def _properties(owned_by=None):
    places = live_properties(owned_by)
    return {
        "properties": places.count(),
        "units": PropertyUnit.objects.filter(deleted_at__isnull=True, property__in=places).count(),
    }


def _tenancies(now, owned_by=None):
    tenancies = Tenancy.objects.live()
    invitations = TenancyInvitation.objects.all()
    if owned_by is not None:
        tenancies = tenancies.in_properties(live_properties(owned_by))
        invitations = invitations.filter(tenancy__in=tenancies)
    today = now.date()
    counts = tenancies.status_counts()
    return {
        "by_status": {status: counts.get(status, 0) for status in TenancyStatus.values},
        "ending_soon": tenancies.with_status(TenancyStatus.ACTIVE)
        .ending_between(today, today + timedelta(days=ENDING_SOON_DAYS))
        .count(),
        "pending_invitations": invitations.pending(now).count(),
        "expired_invitations": invitations.expired(now).count(),
    }


def _recent_activity():
    entries = AccountAccessHistory.objects.with_people().newest_first()[:RECENT_ACTIVITY_COUNT]
    return [
        {
            "action": entry.action,
            "person": entry.user,
            "by": entry.created_by,
            "at": entry.created_at,
        }
        for entry in entries
    ]
