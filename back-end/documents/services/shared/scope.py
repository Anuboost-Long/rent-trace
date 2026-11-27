from rest_framework.exceptions import NotFound, ValidationError

from documents.models import Document, DocumentType
from maintenance.models import MaintenanceIssue
from properties.services.shared.queries import live_properties
from tenancies.models import Tenancy, TenancyParty

NOT_FOUND = "No document with this id."
NEEDS_TENANCY = "A tenancy agreement must name the tenancy it is for."


def find_document_I_own(landlord, document_id, *, lock=False):
    documents = Document.objects.filter(
        property_unit__property__in=live_properties(landlord), deleted_at__isnull=True
    )
    if lock:
        documents = documents.select_for_update(of=("self",))
    found = documents.with_versions().filter(pk=document_id).first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found


def find_document_on_my_tenancy(tenant, tenancy_id, document_id):
    is_member = TenancyParty.objects.filter(tenancy_id=tenancy_id, tenant=tenant).exists()
    found = (
        Document.objects.on_tenancy(tenancy_id).with_versions().filter(pk=document_id).first()
        if is_member
        else None
    )
    if found is None:
        raise NotFound(NOT_FOUND)
    return found


def tenancy_on_unit(unit, tenancy_id):
    if tenancy_id is None:
        return None
    found = Tenancy.objects.live().filter(pk=tenancy_id, property_unit=unit).first()
    if found is None:
        raise NotFound("No tenancy on this unit with this id.")
    return found


def issue_on_unit(unit, issue_id):
    if issue_id is None:
        return None
    found = MaintenanceIssue.objects.filter(
        pk=issue_id, property_unit=unit, deleted_at__isnull=True
    ).first()
    if found is None:
        raise NotFound("No maintenance issue on this unit with this id.")
    return found


def require_tenancy_for(document_type, tenancy):
    if document_type == DocumentType.TENANCY_AGREEMENT and tenancy is None:
        raise ValidationError({"tenancy_id": NEEDS_TENANCY})
