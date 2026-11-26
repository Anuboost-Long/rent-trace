from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from common.models import PartySide
from reviews.models import ReviewRequest, ReviewRoute, ReviewStatus
from reviews.services.shared import notices
from reviews.services.shared.admins import admins_who_can_decide
from reviews.services.shared.decisions import finish, is_expired
from reviews.services.shared.disputes import open_dispute
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import find_evidence_I_am_party_to, reloaded

CANNOT_ESCALATE = "Only a rejected or expired report can be sent to an admin."
ALREADY_ESCALATED = "An admin has already been asked to decide this."


@transaction.atomic
def escalate_evidence(*, user, request_id, reason):
    report = find_evidence_I_am_party_to(user, request_id, lock=True)
    reason = reason.strip()
    side = PartySide.TENANT if report.requested_by_id == user.pk else PartySide.LANDLORD
    now = timezone.now()
    if report.status == ReviewStatus.DISPUTED:
        case = _send_existing_case(report)
    elif is_expired(report):
        case = _open_case_for_expired(report, user, reason, side, now)
    else:
        raise ValidationError({"request": CANNOT_ESCALATE})
    record_transition(
        case,
        ReviewStatus.PENDING_REVIEW,
        "ESCALATE",
        user,
        reason,
        from_status=ReviewStatus.PENDING_REVIEW,
    )
    title = report.current_submission.proposed_condition_version.title
    notices.escalated(case, admins_who_can_decide(), user, title, reason)
    return reloaded(report)


def _send_existing_case(report):
    case = ReviewRequest.objects.cases_for(report).select_for_update().get()
    if case.review_route == ReviewRoute.ADMIN:
        raise ValidationError({"request": ALREADY_ESCALATED})
    case.review_route = ReviewRoute.ADMIN
    case.row_version += 1
    case.save()
    return case


def _open_case_for_expired(report, user, reason, side, now):
    finish(report, ReviewStatus.DISPUTED, user, now=now)
    record_transition(
        report,
        ReviewStatus.DISPUTED,
        "ESCALATE",
        user,
        reason,
        from_status=ReviewStatus.PENDING_REVIEW,
    )
    return open_dispute(report, user, reason, now, side=side, route=ReviewRoute.ADMIN)
