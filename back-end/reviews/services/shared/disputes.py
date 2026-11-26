import uuid

from reviews.models import Dispute, ReviewKind, ReviewRequest, ReviewStatus
from reviews.services.shared.history import record_transition


def open_dispute(report, opener, reason, now, *, side, route):
    case = ReviewRequest.objects.create(
        target=report.target,
        kind=ReviewKind.DISPUTE,
        requested_by=opener,
        requester_side=side,
        review_route=route,
        status=ReviewStatus.PENDING_REVIEW,
        parent_request=report,
        submitted_at=now,
        created_by=opener,
        updated_by=opener,
    )
    Dispute.objects.create(
        request=case,
        origin_request=report,
        opened_by=opener,
        disputed_submission=report.current_submission,
        details=reason,
        created_by=opener,
        correlation_id=uuid.uuid4(),
    )
    record_transition(case, ReviewStatus.PENDING_REVIEW, "OPEN_DISPUTE", opener, reason)
    return case
