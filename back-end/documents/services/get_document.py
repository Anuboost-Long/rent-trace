from rest_framework.exceptions import NotFound

from documents.models import Document
from documents.services.shared.scope import (
    NOT_FOUND,
    find_document_I_own,
    find_document_on_my_tenancy,
)


def get_document_for_landlord(*, landlord, document_id):
    return find_document_I_own(landlord, document_id)


def get_document_for_tenant(*, tenant, tenancy_id, document_id):
    return find_document_on_my_tenancy(tenant, tenancy_id, document_id)


def get_document_for_admin(*, document_id):
    found = Document.objects.filter(pk=document_id, deleted_at__isnull=True).with_versions().first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found
