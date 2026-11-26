from django.utils import timezone
from rest_framework.exceptions import NotFound

from documents.models import Document, DocumentVersion
from properties.services.shared.queries import current_owner_users
from reviews.models import ReviewDecisionType, ReviewerSide, ReviewKind, ReviewRequest, ReviewStatus
from reviews.services.shared import notices
from reviews.services.shared.decisions import (
    finish,
    record_decision,
    require_pending,
    was_already_decided,
)
from reviews.services.shared.history import record_change, record_transition
from tenancies.services.request_housemate import lock_my_tenancy

NO_VERSION = "No document version waiting for your confirmation."


def _find_waiting(tenancy_id, version_id):
    version = (
        DocumentVersion.objects.filter(
            pk=version_id,
            document__tenancy_id=tenancy_id,
            document__deleted_at__isnull=True,
            confirmation_request__kind=ReviewKind.DOCUMENT_CONFIRMATION,
        )
        .select_related("document", "confirmation_request")
        .first()
    )
    if version is None:
        raise NotFound(NO_VERSION)
    request = (
        ReviewRequest.objects.select_for_update(of=("self",))
        .select_related("current_submission", "target")
        .get(pk=version.confirmation_request_id)
    )
    return version, request


def answer_version(tenant, tenancy_id, version_id, *, idempotency_key, reason, confirm):
    """One current tenant of the tenancy confirms the version, or flags it with a reason."""
    tenancy = lock_my_tenancy(tenant, tenancy_id)
    version, request = _find_waiting(tenancy.pk, version_id)
    if not was_already_decided(request, idempotency_key):
        require_pending(request)
        _decide(tenant, tenancy, version, request, idempotency_key, reason, confirm)
    return Document.objects.with_versions().get(pk=version.document_id)


def _decide(tenant, tenancy, version, request, idempotency_key, reason, confirm):
    now = timezone.now()
    document = version.document
    kind = ReviewDecisionType.APPROVE if confirm else ReviewDecisionType.REJECT
    decision = record_decision(
        request,
        tenant,
        kind,
        reason,
        idempotency_key,
        side=ReviewerSide.TENANT,
        submission=request.current_submission,
    )
    status = ReviewStatus.APPROVED if confirm else ReviewStatus.REJECTED
    if confirm:
        _make_current(request, document, version, tenant)
    finish(request, status, tenant, now=now, applied=confirm)
    record_transition(
        request,
        status,
        "CONFIRM" if confirm else "FLAG",
        tenant,
        reason or "Confirmed by the tenant",
        from_status=ReviewStatus.PENDING_REVIEW,
        submission=request.current_submission,
        decision=decision,
    )
    owners = current_owner_users(document.property_unit.property)
    notices.document_confirmation_answered(
        document, owners, tenant, version.title, "confirmed" if confirm else "flagged", reason
    )


def _make_current(request, document, version, tenant):
    before = document.current_version.version_no if document.current_version else None
    record_change(
        request,
        tenant,
        "CONFIRM_DOCUMENT_VERSION",
        {"current_version": before},
        {"current_version": version.version_no},
        "Confirmed by the tenant",
    )
    document.current_version = version
    document.updated_by = tenant
    document.row_version += 1
    document.save()
