from django.core.files.storage import default_storage
from django.db import transaction

from documents.models import Document
from documents.services.shared.scope import find_document_I_own
from documents.services.shared.uploads import check_document_upload, record_file, save_upload
from documents.services.shared.versions import add_version


def add_document_version(*, landlord, document_id, fields, upload):
    mime_type, extension = check_document_upload(upload)
    key = save_upload(upload, f"documents/{document_id}", mime_type, extension)
    try:
        return _record(landlord, document_id, fields, upload, key, mime_type)
    except Exception:
        default_storage.delete(key)
        raise


@transaction.atomic
def _record(landlord, document_id, fields, upload, key, mime_type):
    document = find_document_I_own(landlord, document_id, lock=True)
    add_version(document, landlord, fields, record_file(landlord, upload, key, mime_type))
    return Document.objects.with_versions().get(pk=document.pk)
