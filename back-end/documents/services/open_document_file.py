from django.core.files.storage import default_storage
from rest_framework.exceptions import NotFound

from documents.models import DocumentFile
from properties.services.shared.queries import live_properties
from tenancies.models import TenancyParty

NOT_FOUND = "No file with this id."


def open_document_file(*, user, file_id, as_admin=False):
    """The owner of the unit, a tenant of the document's tenancy, or an admin; others get a 404."""
    link = (
        DocumentFile.objects.filter(
            file_id=file_id, document_version__document__deleted_at__isnull=True
        )
        .select_related("file", "document_version__document__property_unit")
        .first()
    )
    if link is None:
        raise NotFound(NOT_FOUND)
    document = link.document_version.document
    owns = live_properties(user).filter(pk=document.property_unit.property_id).exists()
    is_tenant = (
        document.tenancy_id is not None
        and TenancyParty.objects.filter(tenancy_id=document.tenancy_id, tenant=user).exists()
    )
    if not (as_admin or owns or is_tenant):
        raise NotFound(NOT_FOUND)
    if link.file.deleted_at is not None or not default_storage.exists(link.file.object_key):
        raise NotFound("This file is no longer available.")
    return link.file, default_storage.open(link.file.object_key, "rb")
