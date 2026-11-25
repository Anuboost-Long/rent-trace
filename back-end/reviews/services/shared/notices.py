from notifications.models import NotificationKind as Kind
from notifications.services.shared import notify


def _name(person):
    return f"{person.first_name} {person.last_name}"


def submitted(request, author, owners, title):
    notify(
        owners,
        kind=Kind.CONDITION_EVIDENCE_SUBMITTED,
        title="A tenant added a condition account",
        body=f"{_name(author)} added: {title}. Open the unit to approve or reject it.",
        subject_id=request.pk,
    )


def approved(request, title):
    notify(
        [request.requested_by],
        kind=Kind.CONDITION_EVIDENCE_APPROVED,
        title="Your condition account was approved",
        body=f"Your landlord approved: {title}",
        subject_id=request.pk,
    )


def rejected(request, title, reason):
    notify(
        [request.requested_by],
        kind=Kind.CONDITION_EVIDENCE_REJECTED,
        title="Your condition account was rejected",
        body=f"Your landlord rejected: {title}. Reason: {reason}",
        subject_id=request.pk,
    )
