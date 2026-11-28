from django.core.files.storage import default_storage
from django.db import transaction
from rest_framework.exceptions import NotFound

from documents.models import Document
from documents.services.shared.scope import issue_on_unit
from documents.services.shared.uploads import check_document_upload, record_file, save_upload
from documents.services.shared.versions import add_version
from tenancies.services.request_housemate import lock_my_tenancy

NOT_ON_TENANCY = "No maintenance issue on this tenancy with this id."


def upload_tenant_document(*, tenant, tenancy_id, fields, upload):
    mime_type, extension = check_document_upload(upload)
    key = save_upload(upload, f"documents/tenancy-{tenancy_id}", mime_type, extension)
    try:
        return _record(tenant, tenancy_id, fields, upload, key, mime_type)
    except Exception:
        default_storage.delete(key)
        raise


@transaction.atomic
def _record(tenant, tenancy_id, fields, upload, key, mime_type):
    tenancy = lock_my_tenancy(tenant, tenancy_id)
    issue = issue_on_unit(tenancy.property_unit, fields.get("maintenance_issue_id"))
    if issue is not None and issue.tenancy_id != tenancy.pk:
        raise NotFound(NOT_ON_TENANCY)
    document = Document.objects.create(
        property_unit=tenancy.property_unit,
        tenancy=tenancy,
        maintenance_issue=issue,
        document_type=fields["document_type"],
        created_by=tenant,
        updated_by=tenant,
    )
    stored = record_file(tenant, upload, key, mime_type)
    add_version(document, tenant, fields, stored, by_tenant=True)
    return Document.objects.with_versions().get(pk=document.pk)
