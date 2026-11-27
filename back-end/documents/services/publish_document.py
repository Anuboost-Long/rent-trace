from django.core.files.storage import default_storage
from django.db import transaction

from conditions.services.shared.scope import find_owned_unit
from documents.models import Document
from documents.services.shared.scope import issue_on_unit, require_tenancy_for, tenancy_on_unit
from documents.services.shared.uploads import (
    check_document_upload,
    record_file,
    save_upload,
)
from documents.services.shared.versions import add_version


def publish_document(*, landlord, fields, upload):
    mime_type, extension = check_document_upload(upload)
    key = save_upload(upload, f"documents/{fields['unit_id']}", mime_type, extension)
    try:
        return _record(landlord, fields, upload, key, mime_type)
    except Exception:
        default_storage.delete(key)
        raise


@transaction.atomic
def _record(landlord, fields, upload, key, mime_type):
    unit = find_owned_unit(landlord, fields["unit_id"])
    tenancy = tenancy_on_unit(unit, fields.get("tenancy_id"))
    issue = issue_on_unit(unit, fields.get("maintenance_issue_id"))
    if tenancy is None and issue is not None:
        tenancy = issue.tenancy
    require_tenancy_for(fields["document_type"], tenancy)
    document = Document.objects.create(
        property_unit=unit,
        tenancy=tenancy,
        maintenance_issue=issue,
        document_type=fields["document_type"],
        created_by=landlord,
        updated_by=landlord,
    )
    add_version(document, landlord, fields, record_file(landlord, upload, key, mime_type))
    return Document.objects.with_versions().get(pk=document.pk)
