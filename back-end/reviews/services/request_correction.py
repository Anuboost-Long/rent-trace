import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from common.models import PartySide
from reviews.models import (
    ReviewKind,
    ReviewRequest,
    ReviewRequestScope,
    ReviewRoute,
    ReviewStatus,
    ReviewSubmission,
    ReviewTarget,
)
from reviews.services.shared import notices
from reviews.services.shared.admins import admins_who_can_decide
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import (
    find_note_landlord_may_correct,
    find_note_tenant_may_correct,
    reloaded_correction,
)
from tenancies.services.request_housemate import lock_my_tenancy

ALREADY_WAITING = "A correction is already waiting for this note."


def request_correction(*, user, record_id, fields, tenancy_id=None):
    """A tenant (with a tenancy id) or a landlord asks an admin to correct a note people rely on."""
    return _record(user, record_id, fields, tenancy_id)


@transaction.atomic
def _record(user, record_id, fields, tenancy_id):
    if tenancy_id is None:
        side = PartySide.LANDLORD
        note = find_note_landlord_may_correct(user, record_id)
        tenancy_for_scope = note.tenancy
    else:
        side = PartySide.TENANT
        tenancy_for_scope = lock_my_tenancy(user, tenancy_id)
        note = find_note_tenant_may_correct(tenancy_for_scope.property_unit, record_id)
    waiting = ReviewRequest.objects.corrections().filter(
        target__condition_record=note, status=ReviewStatus.PENDING_REVIEW
    )
    if waiting.exists():
        raise ValidationError({"record_id": ALREADY_WAITING})
    return _create(user, side, note, tenancy_for_scope, fields)


def _create(user, side, note, tenancy, fields):
    now = timezone.now()
    audit = {"created_by": user, "correlation_id": uuid.uuid4()}
    current = note.accepted_version
    request = ReviewRequest.objects.create(
        target=ReviewTarget.objects.get_or_create(condition_record=note, defaults=audit)[0],
        kind=ReviewKind.LOCKED_CORRECTION,
        requested_by=user,
        requester_side=side,
        review_route=ReviewRoute.ADMIN,
        status=ReviewStatus.PENDING_REVIEW,
        submitted_at=now,
        created_by=user,
        updated_by=user,
    )
    submission = ReviewSubmission.objects.create(
        request=request,
        revision_no=1,
        submitted_by=user,
        expected_row_version=note.row_version,
        base_condition_version=current,
        before_values={"title": current.title, "description": current.condition_description},
        proposed_values={
            "title": fields.get("title") or current.title,
            "description": fields["proposed_replacement"],
        },
        what_is_incorrect=fields["what_is_incorrect"],
        proposed_replacement=fields["proposed_replacement"],
        why_change_needed=fields["why_change_needed"],
        reason=fields["why_change_needed"],
        **audit,
    )
    request.current_submission = submission
    request.save()
    ReviewRequestScope.objects.create(request=request, tenancy=tenancy, scope_revision=1, **audit)
    record_transition(
        request,
        ReviewStatus.PENDING_REVIEW,
        "REQUEST_CORRECTION",
        user,
        fields["why_change_needed"],
        submission=submission,
    )
    notices.correction_requested(request, admins_who_can_decide(), user, current.title)
    return reloaded_correction(request)
