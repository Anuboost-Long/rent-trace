from accounts.models import User
from accounts.services.shared.account_rules import has_role
from notifications.models import NotificationKind as Kind
from notifications.services.shared import notify
from properties.services.shared.queries import current_owner_users
from tenancies.services.shared.invitations import place_name


def _name(person):
    return f"{person.first_name} {person.last_name}"


def _tenant_with_email(email):
    person = User.objects.not_deleted().verified().with_email(email).first()
    return person if person and has_role(person, "TENANT") else None


def _owners(tenancy):
    return current_owner_users(tenancy.property_unit.property)


def invitation_sent(invitation, tenancy, actor, *, again, needs_landlord=False):
    invitee = _tenant_with_email(invitation.email_normalized)
    if invitee is None:
        return
    body = f"{_name(actor)} invited you to join {place_name(tenancy)}."
    if needs_landlord:
        body += " The landlord also needs to approve."
    notify(
        [invitee],
        kind=Kind.TENANCY_INVITATION_RECEIVED,
        title="Invitation sent again" if again else "You're invited to join a tenancy",
        body=body,
        subject_id=invitation.pk,
    )


def invitation_accepted(invitation, tenant, *, finished_by=None):
    """Someone joined. The person who asked is told; so are the owners when a tenant asked."""
    recipients = [invitation.created_by] if invitation.created_by else []
    if invitation.requested_by_tenant:
        recipients += _owners(invitation.tenancy)
    notify(
        [
            person
            for person in recipients
            if person.pk not in {tenant.pk, getattr(finished_by, "pk", None)}
        ],
        kind=Kind.TENANCY_INVITATION_ACCEPTED,
        title="Invitation accepted",
        body=f"{_name(tenant)} joined {place_name(invitation.tenancy)}.",
        subject_id=invitation.tenancy_id,
    )


def housemate_requested(tenancy, requester):
    notify(
        _owners(tenancy),
        kind=Kind.TENANCY_HOUSEMATE_REQUESTED,
        title="A tenant asked to add a housemate",
        body=f"{_name(requester)} asked to add someone to {place_name(tenancy)}. Open the tenancy to review it.",
        subject_id=tenancy.pk,
    )


def housemate_decided(invitation, tenancy, *, approved):
    invitee = _tenant_with_email(invitation.email_normalized)
    recipients = [invitation.created_by] + ([invitee] if invitee else [])
    verb = "approved" if approved else "declined"
    notify(
        [person for person in recipients if person is not None],
        kind=Kind.TENANCY_HOUSEMATE_APPROVED if approved else Kind.TENANCY_HOUSEMATE_DECLINED,
        title=f"Housemate request {verb}",
        body=f"The landlord {verb} the request to add a housemate to {place_name(tenancy)}.",
        subject_id=tenancy.pk,
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


def terms_changed(tenancy, tenants):
    """Tells the tenants the terms moved. The text carries no amounts; they open the tenancy."""
    notify(
        tenants,
        kind=Kind.TENANCY_TERMS_CHANGED,
        title="The terms of your tenancy changed",
        body=f"The dates, rent or bond for your tenancy at {place_name(tenancy)} changed. Open it to see the new terms.",
        subject_id=tenancy.pk,
    )


def terms_proposed(tenancy, tenants):
    """Tells the tenants a rent or bond increase needs their answer. No amounts in the text."""
    notify(
        tenants,
        kind=Kind.TENANCY_TERMS_PROPOSED,
        title="Your landlord proposed new rent or bond",
        body=f"A change to the rent or bond for your tenancy at {place_name(tenancy)} needs your approval. Open it to review.",
        subject_id=tenancy.pk,
    )


def terms_applied(tenancy, proposer, tenants):
    notify(
        [proposer] if proposer else [],
        kind=Kind.TENANCY_TERMS_APPLIED,
        title="Your rent or bond change was approved",
        body=f"Every tenant approved the change for {place_name(tenancy)}. It now applies.",
        subject_id=tenancy.pk,
    )
    terms_changed(tenancy, tenants)


def terms_declined(tenancy, proposer, decliner):
    notify(
        [proposer] if proposer else [],
        kind=Kind.TENANCY_TERMS_DECLINED,
        title="A tenant declined your rent or bond change",
        body=f"{_name(decliner)} declined the change for {place_name(tenancy)}. Nothing changed.",
        subject_id=tenancy.pk,
    )
