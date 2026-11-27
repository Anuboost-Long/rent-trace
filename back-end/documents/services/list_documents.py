from rest_framework.exceptions import NotFound

from conditions.services.shared.scope import find_owned_unit
from documents.models import Document
from tenancies.models import TenancyParty


def list_documents_for_unit(*, landlord, unit_id):
    find_owned_unit(landlord, unit_id)
    return Document.objects.on_unit(unit_id).with_versions().order_by("-id")


def list_documents_for_tenancy(*, tenant, tenancy_id):
    is_member = TenancyParty.objects.filter(tenancy_id=tenancy_id, tenant=tenant).exists()
    if not is_member:
        raise NotFound("No tenancy with this id.")
    return Document.objects.on_tenancy(tenancy_id).with_versions().order_by("-id")


def list_documents_for_admin(*, unit_id):
    return Document.objects.on_unit(unit_id).with_versions().order_by("-id")
