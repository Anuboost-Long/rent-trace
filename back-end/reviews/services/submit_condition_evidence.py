import uuid

from django.db import transaction
from django.utils import timezone

from common.models import PartySide
from conditions.models import ConditionRecord, ConditionRecordType, ConditionVersion, SourceType
from properties.services.shared.queries import current_owner_users
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
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import reloaded
from tenancies.services.request_housemate import lock_my_tenancy


@transaction.atomic
def submit_condition_evidence(*, user, tenancy_id, fields):
    tenancy = lock_my_tenancy(user, tenancy_id)
    now = timezone.now()
    audit = {"created_by": user, "correlation_id": uuid.uuid4()}
    note = ConditionRecord.objects.create(
        property_unit=tenancy.property_unit,
        tenancy=tenancy,
        record_type=ConditionRecordType.DISCREPANCY,
        created_by=user,
        updated_by=user,
    )
    version = ConditionVersion.objects.create(
        condition_record=note,
        version_no=1,
        title=fields["title"],
        condition_description=fields.get("description") or None,
        source_type=SourceType.TENANT,
        observed_at=fields["observed_at"],
        submitted_by=user,
        submitted_at=now,
        **audit,
    )
    request = ReviewRequest.objects.create(
        target=ReviewTarget.objects.create(condition_record=note, **audit),
        kind=ReviewKind.EVIDENCE_REVIEW,
        requested_by=user,
        requester_side=PartySide.TENANT,
        review_route=ReviewRoute.OPPOSITE_SIDE,
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
        proposed_condition_version=version,
        proposed_values={
            "title": version.title,
            "description": version.condition_description,
            "observed_at": version.observed_at.isoformat(),
        },
        **audit,
    )
    request.current_submission = submission
    request.save()
    ReviewRequestScope.objects.create(request=request, tenancy=tenancy, scope_revision=1, **audit)
    record_transition(
        request,
        ReviewStatus.PENDING_REVIEW,
        "SUBMIT",
        user,
        "Tenant added a condition account",
        submission=submission,
    )
    notices.submitted(
        request, user, current_owner_users(tenancy.property_unit.property), version.title
    )
    return reloaded(request)
