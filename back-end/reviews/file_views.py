from django.http import FileResponse
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from properties.landlord_views import LandlordView
from reviews import dtos, resources, services
from tenancies.tenant_views import TenantView
from tenancies.views import validated

CONTENT_CACHE = "private, max-age=3600"


def _photo_response(user, file_id, *, as_admin=False):
    stored, content = services.open_evidence_photo(user=user, file_id=file_id, as_admin=as_admin)
    response = FileResponse(content, content_type=stored.mime_type, filename=stored.original_name)
    response["Cache-Control"] = CONTENT_CACHE
    return response


class AddEvidencePhotoView(TenantView):
    required_permissions = {"POST": "reviews.submit"}
    parser_classes = [MultiPartParser]

    @extend_schema(
        operation_id="tenant_condition_evidence_add_photo",
        request={"multipart/form-data": dtos.AddEvidencePhotoDto},
        responses={201: resources.EvidenceResource},
    )
    def post(self, request, tenancy_id, request_id):
        fields = validated(dtos.AddEvidencePhotoDto, request.data)
        report = services.add_evidence_photo(
            user=request.user, request_id=request_id, upload=fields["file"]
        )
        return Response(resources.EvidenceResource(report).data, status=201)


class TenantEvidencePhotoView(TenantView):
    required_permissions = {"GET": "reviews.view"}

    @extend_schema(
        operation_id="tenant_condition_evidence_photo",
        responses={(200, "application/octet-stream"): bytes},
    )
    def get(self, request, tenancy_id, file_id):
        return _photo_response(request.user, file_id)


class LandlordEvidencePhotoView(LandlordView):
    required_permissions = {"GET": "reviews.view"}

    @extend_schema(
        operation_id="landlord_condition_evidence_photo",
        responses={(200, "application/octet-stream"): bytes},
    )
    def get(self, request, file_id):
        return _photo_response(request.user, file_id)


class AdminEvidencePhotoView(PermissionedView):
    required_permissions = {"GET": "reviews.admin_review"}

    @extend_schema(
        operation_id="admin_review_case_photo",
        responses={(200, "application/octet-stream"): bytes},
    )
    def get(self, request, file_id):
        return _photo_response(request.user, file_id, as_admin=True)
