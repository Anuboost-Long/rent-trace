from accounts.models import User
from accounts.services.shared.account_rules import has_role
from notifications.models import NotificationKind as Kind
from notifications.services.shared import notify
from tenancies.services.shared.invitations import place_name


def _name(person):
    return f"{person.first_name} {person.last_name}"


def _tenant_with_email(email):
    person = User.objects.not_deleted().verified().with_email(email).first()
    return person if person and has_role(person, "TENANT") else None


def invitation_sent(invitation, tenancy, actor, *, again):
    invitee = _tenant_with_email(invitation.email_normalized)
    if invitee is None:
        return
    notify(
        [invitee],
        kind=Kind.TENANCY_INVITATION_RECEIVED,
        title="Invitation sent again" if again else "You're invited to join a tenancy",
        body=f"{_name(actor)} invited you to join {place_name(tenancy)}.",
        subject_id=invitation.pk,
    )


def invitation_accepted(invitation, tenant):
    sender = invitation.created_by
    if sender is None or sender.pk == tenant.pk:
        return
    notify(
        [sender],
        kind=Kind.TENANCY_INVITATION_ACCEPTED,
        title="Invitation accepted",
        body=f"{_name(tenant)} joined {place_name(invitation.tenancy)}.",
        subject_id=invitation.tenancy_id,
    )


def _tell_tenants(tenancy, tenants, kind, title, verb):
    notify(
        tenants,
        kind=kind,
        title=title,
        body=f"Your tenancy at {place_name(tenancy)} {verb}.",
        subject_id=tenancy.pk,
    )


def tenancy_started(tenancy, tenants):
    _tell_tenants(tenancy, tenants, Kind.TENANCY_STARTED, "Your tenancy has started", "has started")


def tenancy_ended(tenancy, tenants):
    _tell_tenants(tenancy, tenants, Kind.TENANCY_ENDED, "Your tenancy has ended", "has ended")


def tenancy_cancelled(tenancy, tenants):
    _tell_tenants(
        tenancy, tenants, Kind.TENANCY_CANCELLED, "Your tenancy was cancelled", "was cancelled"
    )
