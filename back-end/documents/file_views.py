from django.http import FileResponse
from drf_spectacular.utils import extend_schema

from accounts.security.permissioned_view import PermissionedView
from documents import services
from properties.landlord_views import LandlordView
from tenancies.tenant_views import TenantView

CONTENT_CACHE = "private, max-age=3600"


def _response(user, file_id, *, as_admin=False):
    stored, content = services.open_document_file(user=user, file_id=file_id, as_admin=as_admin)
    response = FileResponse(content, content_type=stored.mime_type, filename=stored.original_name)
    response["Cache-Control"] = CONTENT_CACHE
    return response


class LandlordDocumentFileView(LandlordView):
    required_permissions = {"GET": "documents.view"}

    @extend_schema(
        operation_id="landlord_document_file",
        responses={(200, "application/octet-stream"): bytes},
    )
    def get(self, request, file_id):
        return _response(request.user, file_id)


class TenantDocumentFileView(TenantView):
    required_permissions = {"GET": "documents.view"}

    @extend_schema(
        operation_id="tenant_document_file",
        responses={(200, "application/octet-stream"): bytes},
    )
    def get(self, request, tenancy_id, file_id):
        return _response(request.user, file_id)


class AdminDocumentFileView(PermissionedView):
    required_permissions = {"GET": "documents.admin_view"}

    @extend_schema(
        operation_id="admin_document_file",
        responses={(200, "application/octet-stream"): bytes},
    )
    def get(self, request, file_id):
        return _response(request.user, file_id, as_admin=True)
