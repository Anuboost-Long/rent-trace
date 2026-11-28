from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from common.models import PartySide
from documents.models import DocumentVersion
from properties.services.shared.queries import current_owner_users, live_properties
from reviews.models import ReviewRequest, ReviewRoute, ReviewStatus
from reviews.services.shared import notices
from reviews.services.shared.admins import admins_who_can_decide
from reviews.services.shared.decisions import finish, is_expired
from reviews.services.shared.disputes import open_dispute
from reviews.services.shared.history import record_transition
from tenancies.services.request_housemate import lock_my_tenancy

NOT_FOUND = "No document version waiting for an answer with this id."
CANNOT_ESCALATE = "Only a flagged or expired version can be sent to an admin."
ALREADY_ESCALATED = "An admin has already been asked to decide this."
NEWER_VERSION = "A newer version was published, so this one can't be sent to an admin."


def _versions_with_confirmation():
    return DocumentVersion.objects.filter(
        confirmation_request__isnull=False, document__deleted_at__isnull=True
    ).select_related("document__property_unit__property", "document__tenancy")


def _find(versions, version_id):
    found = versions.filter(pk=version_id).first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found


@transaction.atomic
def escalate_for_tenant(*, tenant, tenancy_id, version_id, reason):
    tenancy = lock_my_tenancy(tenant, tenancy_id)
    versions = _versions_with_confirmation().filter(document__tenancy_id=tenancy.pk)
    return _escalate(_find(versions, version_id), tenant, PartySide.TENANT, reason)


@transaction.atomic
def escalate_for_landlord(*, landlord, version_id, reason):
    versions = _versions_with_confirmation().filter(
        document__property_unit__property__in=live_properties(landlord)
    )
    return _escalate(_find(versions, version_id), landlord, PartySide.LANDLORD, reason)


def _escalate(version, user, side, reason):
    report = ReviewRequest.objects.select_for_update(of=("self",)).get(
        pk=version.confirmation_request_id
    )
    document = version.document
    _require_escalatable(report, version)
    reason = reason.strip()
    now = timezone.now()
    before = report.status
    finish(report, ReviewStatus.DISPUTED, user, now=now)
    record_transition(report, ReviewStatus.DISPUTED, "ESCALATE", user, reason, from_status=before)
    case = open_dispute(report, user, reason, now, side=side, route=ReviewRoute.ADMIN)
    owners = current_owner_users(document.property_unit.property)
    others = tenants_of(document) if side == PartySide.LANDLORD else owners
    notices.document_escalated(case, admins_who_can_decide(), user, others, version.title, reason)
    return document


def tenants_of(document):
    return [party.tenant for party in document.tenancy.parties.current().select_related("tenant")]


def _require_escalatable(report, version):
    if ReviewRequest.objects.cases_for(report).exists() or report.status == ReviewStatus.DISPUTED:
        raise ValidationError({"request": ALREADY_ESCALATED})
    if report.status != ReviewStatus.REJECTED and not is_expired(report):
        raise ValidationError({"request": CANNOT_ESCALATE})
    newest = version.document.versions.aggregate(newest=Max("version_no"))["newest"]
    if version.version_no != newest:
        raise ValidationError({"request": NEWER_VERSION})
