from maintenance.services.shared.parties import current_owner_users
from notifications.models import NotificationKind as Kind
from notifications.services.shared import notify


def _name(person):
    return f"{person.first_name} {person.last_name}"


def reported(issue, reporter):
    notify(
        current_owner_users(issue),
        kind=Kind.MAINTENANCE_REPORTED,
        title="New maintenance issue",
        body=f"{_name(reporter)} reported: {issue.title}",
        subject_id=issue.pk,
    )


def acknowledged(issue):
    notify(
        [issue.reported_by],
        kind=Kind.MAINTENANCE_ACKNOWLEDGED,
        title="Your maintenance issue was acknowledged",
        body=f"Your landlord has seen: {issue.title}",
        subject_id=issue.pk,
    )


def started(issue):
    notify(
        [issue.reported_by],
        kind=Kind.MAINTENANCE_STARTED,
        title="Work has started on your issue",
        body=f"Work has started on: {issue.title}",
        subject_id=issue.pk,
    )


def closure_proposed(issue, proposer, recipients):
    notify(
        recipients,
        kind=Kind.MAINTENANCE_CLOSURE_PROPOSED,
        title="Closing a maintenance issue was proposed",
        body=f"{_name(proposer)} proposed closing: {issue.title}. Open it to approve or reject.",
        subject_id=issue.pk,
    )


def closure_rejected(issue, proposer, rejecter):
    notify(
        [proposer],
        kind=Kind.MAINTENANCE_CLOSURE_REJECTED,
        title="Closing the issue was rejected",
        body=f"{_name(rejecter)} rejected closing: {issue.title}. It stays open.",
        subject_id=issue.pk,
    )


def closed(issue, recipients):
    notify(
        recipients,
        kind=Kind.MAINTENANCE_CLOSED,
        title="A maintenance issue was closed",
        body=f"Closed: {issue.title}",
        subject_id=issue.pk,
    )
