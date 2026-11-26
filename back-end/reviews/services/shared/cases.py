import uuid

from django.utils import timezone
from rest_framework.exceptions import NotFound

from properties.services.shared.queries import current_owner_users
from reviews.models import (
    DisputeOutcome,
    DisputeResolution,
    ReviewDecisionType,
    ReviewerSide,
    ReviewRequest,
    ReviewStatus,
)
from reviews.services.shared import notices
from reviews.services.shared.acceptance import accept_version
from reviews.services.shared.decisions import (
    finish,
    record_decision,
    require_pending,
    was_already_decided,
)
from reviews.services.shared.history import record_transition

NOT_FOUND = "No case with this id."


def find_admin_case(case_id, *, lock=False):
    cases = ReviewRequest.objects.admin_cases().select_related("dispute", "parent_request")
    if lock:
        cases = cases.select_for_update(of=("self",))
    found = cases.filter(pk=case_id).first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found


def decide_case(admin, case, *, approve, reason, idempotency_key):
    """The admin's answer sits on the dispute case; the report it was about follows."""
    if was_already_decided(case, idempotency_key):
        return case
    require_pending(case)
    report = case.parent_request
    submission = report.current_submission
    version = submission.proposed_condition_version
    now = timezone.now()
    kind = ReviewDecisionType.APPROVE if approve else ReviewDecisionType.REJECT
    decision = record_decision(
        case, admin, kind, reason, idempotency_key, side=ReviewerSide.ADMIN, submission=submission
    )
    if approve:
        accept_version(case, admin, version, reason)
    status = ReviewStatus.APPROVED if approve else ReviewStatus.REJECTED
    action = "ADMIN_APPROVE" if approve else "ADMIN_REJECT"
    finish(case, status, admin, now=now, applied=approve)
    record_transition(
        case,
        status,
        action,
        admin,
        reason,
        from_status=ReviewStatus.PENDING_REVIEW,
        submission=submission,
        decision=decision,
    )
    finish(report, status, admin, now=now, applied=approve)
    record_transition(report, status, action, admin, reason, from_status=ReviewStatus.DISPUTED)
    DisputeResolution.objects.create(
        dispute=case.dispute,
        resolution_request=case,
        outcome=DisputeOutcome.ADMIN_APPROVED if approve else DisputeOutcome.ADMIN_REJECTED,
        result_condition_version=version if approve else None,
        reason=reason,
        created_by=admin,
        correlation_id=uuid.uuid4(),
    )
    place = report.target.condition_record.property_unit.property
    owners = current_owner_users(place)
    notices.decided(report, owners, version.title, "approved" if approve else "rejected", reason)
    return case
