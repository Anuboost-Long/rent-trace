import uuid

from django.db.models import Max
from django.utils import timezone

from common.models import PartySide
from documents.models import DocumentFile, DocumentType, DocumentVersion
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
from reviews.services.shared.decisions import finish
from reviews.services.shared.history import record_transition

NEEDS_CONSENT = {DocumentType.TENANCY_AGREEMENT}


def needs_consent(document):
    return document.document_type in NEEDS_CONSENT and document.tenancy_id is not None


def add_version(document, actor, fields, stored_file, *, by_tenant=False):
    """Adds the next numbered version, then makes it current or asks the tenants to confirm it."""
    now = timezone.now()
    audit = {"created_by": actor, "correlation_id": uuid.uuid4()}
    last = document.versions.aggregate(last=Max("version_no"))["last"] or 0
    previous = document.versions.filter(version_no=last).first()
    version = DocumentVersion.objects.create(
        document=document,
        version_no=last + 1,
        supersedes_version=previous,
        title=fields["title"],
        description=fields.get("description") or None,
        document_date=fields.get("document_date"),
        uploaded_by=actor,
        **audit,
    )
    DocumentFile.objects.create(document_version=version, file=stored_file, created_by=actor)
    if needs_consent(document):
        _ask_to_confirm(document, version, actor, now, audit)
    else:
        _make_current(document, version, actor)
        if by_tenant:
            owners = current_owner_users(document.property_unit.property)
            notices.document_added_by_tenant(document, owners, actor, version.title)
        else:
            notices.document_added(document, version.title)
    return version


def _make_current(document, version, actor):
    document.current_version = version
    document.updated_by = actor
    document.row_version += 1
    document.save()


def _ask_to_confirm(document, version, actor, now, audit):
    superseded = ReviewRequest.objects.filter(
        target__document=document,
        kind=ReviewKind.DOCUMENT_CONFIRMATION,
        status__in=[ReviewStatus.PENDING_REVIEW, ReviewStatus.DISPUTED],
    )
    for older in superseded:
        older_status = older.status
        for case in ReviewRequest.objects.cases_for(older).filter(
            status=ReviewStatus.PENDING_REVIEW
        ):
            finish(case, ReviewStatus.CANCELLED, actor, now=now)
            record_transition(
                case,
                ReviewStatus.CANCELLED,
                "SUPERSEDE",
                actor,
                "A newer version was published",
                from_status=ReviewStatus.PENDING_REVIEW,
            )
        finish(older, ReviewStatus.CANCELLED, actor, now=now)
        record_transition(
            older,
            ReviewStatus.CANCELLED,
            "SUPERSEDE",
            actor,
            "A newer version was published",
            from_status=older_status,
        )
    target = ReviewTarget.objects.get_or_create(document=document, defaults=audit)[0]
    request = ReviewRequest.objects.create(
        target=target,
        kind=ReviewKind.DOCUMENT_CONFIRMATION,
        requested_by=actor,
        requester_side=PartySide.LANDLORD,
        review_route=ReviewRoute.OPPOSITE_SIDE,
        status=ReviewStatus.PENDING_REVIEW,
        submitted_at=now,
        created_by=actor,
        updated_by=actor,
    )
    submission = ReviewSubmission.objects.create(
        request=request,
        revision_no=1,
        submitted_by=actor,
        expected_row_version=document.row_version,
        base_document_version=document.current_version,
        proposed_document_version=version,
        proposed_values={"title": version.title},
        **audit,
    )
    request.current_submission = submission
    request.save()
    ReviewRequestScope.objects.create(
        request=request, tenancy=document.tenancy, scope_revision=1, **audit
    )
    version.confirmation_request = request
    version.save()
    record_transition(
        request,
        ReviewStatus.PENDING_REVIEW,
        "PUBLISH",
        actor,
        "Published for confirmation",
        submission=submission,
    )
    notices.document_confirmation_requested(document, version.title)
