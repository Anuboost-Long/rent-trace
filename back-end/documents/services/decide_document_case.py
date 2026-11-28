from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from documents.models import Document
from documents.services.escalate_document_version import tenants_of
from documents.services.shared.confirmation import make_current
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
from reviews.services.shared.decisions import (
    finish,
    record_decision,
    require_pending,
    was_already_decided,
)
from reviews.services.shared.history import record_transition

NOT_FOUND = "No document case with this id."
NEWER_VERSION = "A newer version was published, so this case can no longer change what is current."


def find_document_case(case_id, *, lock=False):
    cases = ReviewRequest.objects.document_cases().select_related("dispute", "parent_request")
    if lock:
        cases = cases.select_for_update(of=("self",))
    found = cases.filter(pk=case_id).first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found


@transaction.atomic
def decide_document_case(*, admin, case_id, approve, reason, idempotency_key):
    """Confirming makes the flagged version current; rejecting leaves the flag standing."""
    case = find_document_case(case_id, lock=True)
    if was_already_decided(case, idempotency_key):
        return case
    require_pending(case)
    report = ReviewRequest.objects.select_for_update(of=("self",)).get(pk=case.parent_request_id)
    version = report.current_submission.proposed_document_version
    document = Document.objects.select_for_update(of=("self",)).get(pk=version.document_id)
    newest = document.versions.aggregate(newest=Max("version_no"))["newest"]
    if approve and version.version_no != newest:
        raise ValidationError({"case": NEWER_VERSION})
    now = timezone.now()
    submission = report.current_submission
    kind = ReviewDecisionType.APPROVE if approve else ReviewDecisionType.REJECT
    decision = record_decision(
        case, admin, kind, reason, idempotency_key, side=ReviewerSide.ADMIN, submission=submission
    )
    if approve:
        make_current(
            case,
            document,
            version,
            admin,
            action="ADMIN_CONFIRM_DOCUMENT_VERSION",
            reason=reason,
        )
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
        result_document_version=version if approve else None,
        reason=reason,
        created_by=admin,
        correlation_id=case.dispute.correlation_id,
    )
    people = [*current_owner_users(document.property_unit.property), *tenants_of(document)]
    outcome = "confirmed" if approve else "upheld the flag on"
    notices.document_decided(document, people, version.title, outcome, reason)
    return case


def list_document_cases(*, status=None):
    cases = ReviewRequest.objects.document_cases().filter(
        status=status or ReviewStatus.PENDING_REVIEW
    )
    return cases.with_document_case_details().order_by("submitted_at", "id")
