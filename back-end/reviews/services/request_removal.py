import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from common.models import PartySide
from reviews.models import (
    RemovalRequestItem,
    ReviewKind,
    ReviewRequest,
    ReviewRequestScope,
    ReviewRoute,
    ReviewStatus,
    ReviewSubmission,
    ReviewTarget,
)
from reviews.services.shared import notices
from reviews.services.shared.admins import admins_who_can_decide_removals
from reviews.services.shared.history import record_transition
from reviews.services.shared.scope import (
    find_records_landlord_may_remove,
    find_records_tenant_may_remove,
    reloaded_removal,
)
from tenancies.services.request_housemate import lock_my_tenancy

ALREADY_WAITING = "A removal request is already waiting for one of these records."


def request_removal(*, user, record_ids, reason, include_descendants=True, tenancy_id=None):
    """A tenant (with a tenancy id) or a landlord asks an admin to hide condition records."""
    return _record(user, record_ids, reason.strip(), include_descendants, tenancy_id)


@transaction.atomic
def _record(user, record_ids, reason, include_descendants, tenancy_id):
    if tenancy_id is None:
        side = PartySide.LANDLORD
        records = find_records_landlord_may_remove(user, record_ids)
        tenancy = None
    else:
        side = PartySide.TENANT
        tenancy = lock_my_tenancy(user, tenancy_id)
        records = find_records_tenant_may_remove(tenancy.property_unit, user, record_ids)
    waiting = RemovalRequestItem.objects.filter(
        target__condition_record__in=records, request__status=ReviewStatus.PENDING_REVIEW
    )
    if waiting.exists():
        raise ValidationError({"record_ids": ALREADY_WAITING})
    return _create(user, side, records, tenancy, reason, include_descendants)


def _create(user, side, records, tenancy, reason, include_descendants):
    now = timezone.now()
    audit = {"created_by": user, "correlation_id": uuid.uuid4()}
    targets = [
        ReviewTarget.objects.get_or_create(condition_record=record, defaults=audit)[0]
        for record in records
    ]
    request = ReviewRequest.objects.create(
        target=targets[0],
        kind=ReviewKind.DATA_REMOVAL,
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
        proposed_values={"record_ids": [record.pk for record in records]},
        reason=reason,
        **audit,
    )
    request.current_submission = submission
    request.save()
    for target in targets:
        RemovalRequestItem.objects.create(
            request=request,
            target=target,
            include_descendants=include_descendants,
            requested_reason=reason,
            **audit,
        )
    scope_tenancy = tenancy or records[0].tenancy
    if scope_tenancy is not None:
        ReviewRequestScope.objects.create(
            request=request, tenancy=scope_tenancy, scope_revision=1, **audit
        )
    record_transition(
        request,
        ReviewStatus.PENDING_REVIEW,
        "REQUEST_REMOVAL",
        user,
        reason,
        submission=submission,
    )
    notices.removal_requested(request, admins_who_can_decide_removals(), user, len(targets))
    return reloaded_removal(request)
