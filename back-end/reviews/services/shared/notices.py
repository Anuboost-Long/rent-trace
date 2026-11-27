from notifications.models import NotificationKind as Kind
from notifications.services.shared import notify


def _tenancy_id(request):
    return request.target.condition_record.tenancy_id


def _scope_tenancy_id(request):
    scope = request.scopes.first()
    return scope.tenancy_id if scope else None


def _name(person):
    return f"{person.first_name} {person.last_name}"


def submitted(request, author, owners, title):
    notify(
        owners,
        kind=Kind.CONDITION_EVIDENCE_SUBMITTED,
        title="A tenant added a condition account",
        body=f"{_name(author)} added: {title}. Open the unit to approve or reject it.",
        subject_id=_tenancy_id(request),
    )


def approved(request, title):
    notify(
        [request.requested_by],
        kind=Kind.CONDITION_EVIDENCE_APPROVED,
        title="Your condition account was approved",
        body=f"Your landlord approved: {title}",
        subject_id=_tenancy_id(request),
    )


def rejected(request, title, reason):
    notify(
        [request.requested_by],
        kind=Kind.CONDITION_EVIDENCE_REJECTED,
        title="Your condition account was rejected",
        body=f"Your landlord rejected: {title}. Reason: {reason}",
        subject_id=_tenancy_id(request),
    )


def escalated(case, admins, escalator, title, reason):
    notify(
        admins,
        kind=Kind.REVIEW_CASE_ESCALATED,
        title="A condition report needs an admin decision",
        body=f"{_name(escalator)} asked for a decision on: {title}. Reason: {reason}",
        subject_id=case.pk,
    )


def decided(report, owners, title, outcome, reason):
    notify(
        [report.requested_by, *owners],
        kind=Kind.REVIEW_CASE_DECIDED,
        title=f"An admin {outcome} a condition report",
        body=f"An admin {outcome}: {title}. Reason: {reason}",
        subject_id=_tenancy_id(report),
    )


def information_requested(request, title, reason):
    notify(
        [request.requested_by],
        kind=Kind.CONDITION_EVIDENCE_INFO_REQUESTED,
        title="Your landlord asked for more information",
        body=f"About: {title}. They asked: {reason}",
        subject_id=_tenancy_id(request),
    )


def information_provided(request, author, owners, title, message):
    notify(
        owners,
        kind=Kind.CONDITION_EVIDENCE_INFO_PROVIDED,
        title="A tenant answered your question",
        body=f"{_name(author)} replied about: {title}. {message}",
        subject_id=_tenancy_id(request),
    )


def correction_requested(request, admins, asker, title):
    notify(
        admins,
        kind=Kind.CONDITION_CORRECTION_REQUESTED,
        title="A condition note needs a correction decision",
        body=f"{_name(asker)} asked for a correction to: {title}.",
        subject_id=request.pk,
    )


def correction_decided(request, owners, title, outcome, reason):
    notify(
        [request.requested_by, *owners],
        kind=Kind.CONDITION_CORRECTION_DECIDED,
        title=f"An admin {outcome} a condition correction",
        body=f"An admin {outcome} the correction to: {title}. Reason: {reason}",
        subject_id=_scope_tenancy_id(request),
    )
