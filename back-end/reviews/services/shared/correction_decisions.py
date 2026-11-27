import uuid

from django.db.models import Max
from django.utils import timezone

from conditions.models import ConditionVersion, SourceType
from properties.services.shared.queries import current_owner_users
from reviews.models import ReviewDecisionType, ReviewerSide, ReviewStatus
from reviews.services.shared import notices
from reviews.services.shared.acceptance import accept_version
from reviews.services.shared.decisions import (
    finish,
    move,
    record_decision,
    require_pending,
    was_already_decided,
)
from reviews.services.shared.history import record_transition


def decide_correction(admin, request, *, approve, reason, idempotency_key):
    """The admin's answer. A note that changed after the request was written makes it STALE."""
    if was_already_decided(request, idempotency_key):
        return request
    require_pending(request)
    submission = request.current_submission
    note = request.target.condition_record
    if note.row_version != submission.expected_row_version:
        move(request, ReviewStatus.STALE, admin)
        record_transition(
            request,
            ReviewStatus.STALE,
            "MARK_STALE",
            admin,
            "The note changed after this was asked",
            from_status=ReviewStatus.PENDING_REVIEW,
            submission=submission,
        )
        return request
    now = timezone.now()
    kind = ReviewDecisionType.APPROVE if approve else ReviewDecisionType.REJECT
    decision = record_decision(
        request, admin, kind, reason, idempotency_key, side=ReviewerSide.ADMIN
    )
    current = note.accepted_version
    if approve:
        accept_version(request, admin, _corrected_version(request, note, current, now), reason)
    status = ReviewStatus.APPROVED if approve else ReviewStatus.REJECTED
    finish(request, status, admin, now=now, applied=approve)
    record_transition(
        request,
        status,
        "ADMIN_APPROVE" if approve else "ADMIN_REJECT",
        admin,
        reason,
        from_status=ReviewStatus.PENDING_REVIEW,
        submission=submission,
        decision=decision,
    )
    owners = current_owner_users(note.property_unit.property)
    notices.correction_decided(
        request, owners, current.title, "approved" if approve else "rejected", reason
    )
    return request


def _corrected_version(request, note, current, now):
    proposed = request.current_submission.proposed_values
    last = note.versions.aggregate(last=Max("version_no"))["last"]
    return ConditionVersion.objects.create(
        condition_record=note,
        version_no=last + 1,
        supersedes_version=current,
        title=proposed["title"],
        condition_description=proposed["description"],
        source_type=SourceType.TENANT
        if request.requester_side == "TENANT"
        else SourceType.LANDLORD,
        observed_at=current.observed_at,
        submitted_by=request.requested_by,
        submitted_at=now,
        created_by=request.requested_by,
        correlation_id=uuid.uuid4(),
    )
