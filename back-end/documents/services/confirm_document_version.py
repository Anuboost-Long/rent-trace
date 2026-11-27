from django.db import transaction

from documents.services.shared.confirmation import answer_version


@transaction.atomic
def confirm_document_version(*, tenant, tenancy_id, version_id, idempotency_key):
    return answer_version(
        tenant, tenancy_id, version_id, idempotency_key=idempotency_key, reason=None, confirm=True
    )
