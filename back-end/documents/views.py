from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from documents import dtos, resources, services
from properties.landlord_views import LandlordView
from tenancies.tenant_views import TenantView
from tenancies.views import validated


class LandlordDocumentsView(LandlordView):
    required_permissions = {"GET": "documents.view", "POST": "documents.publish"}
    parser_classes = [MultiPartParser]

    @extend_schema(
        operation_id="landlord_documents_list",
        parameters=[dtos.DocumentListQueryDto],
        responses=resources.DocumentResource(many=True),
    )
    def get(self, request):
        query = validated(dtos.DocumentListQueryDto, request.query_params)
        found = services.list_documents_for_unit(landlord=request.user, unit_id=query["unit_id"])
        return Response(resources.DocumentResource(found, many=True).data)

    @extend_schema(
        operation_id="landlord_document_publish",
        request={"multipart/form-data": dtos.PublishDocumentDto},
        responses={201: resources.DocumentResource},
    )
    def post(self, request):
        fields = validated(dtos.PublishDocumentDto, request.data)
        published = services.publish_document(
            landlord=request.user, fields=fields, upload=fields["file"]
        )
        return Response(resources.DocumentResource(published).data, status=201)


class LandlordDocumentView(LandlordView):
    required_permissions = {"GET": "documents.view"}

    @extend_schema(operation_id="landlord_document_detail", responses=resources.DocumentResource)
    def get(self, request, document_id):
        found = services.get_document_for_landlord(landlord=request.user, document_id=document_id)
        return Response(resources.DocumentResource(found).data)


class LandlordDocumentVersionsView(LandlordView):
    required_permissions = {"POST": "documents.publish"}
    parser_classes = [MultiPartParser]

    @extend_schema(
        operation_id="landlord_document_add_version",
        request={"multipart/form-data": dtos.AddVersionDto},
        responses={201: resources.DocumentResource},
    )
    def post(self, request, document_id):
        fields = validated(dtos.AddVersionDto, request.data)
        added = services.add_document_version(
            landlord=request.user, document_id=document_id, fields=fields, upload=fields["file"]
        )
        return Response(resources.DocumentResource(added).data, status=201)


class TenantDocumentsView(TenantView):
    required_permissions = {"GET": "documents.view"}

    @extend_schema(
        operation_id="tenant_documents_list", responses=resources.DocumentResource(many=True)
    )
    def get(self, request, tenancy_id):
        found = services.list_documents_for_tenancy(tenant=request.user, tenancy_id=tenancy_id)
        return Response(resources.DocumentResource(found, many=True).data)


class TenantDocumentView(TenantView):
    required_permissions = {"GET": "documents.view"}

    @extend_schema(operation_id="tenant_document_detail", responses=resources.DocumentResource)
    def get(self, request, tenancy_id, document_id):
        found = services.get_document_for_tenant(
            tenant=request.user, tenancy_id=tenancy_id, document_id=document_id
        )
        return Response(resources.DocumentResource(found).data)


class ConfirmVersionView(TenantView):
    required_permissions = {"POST": "documents.confirm"}

    @extend_schema(
        operation_id="tenant_document_confirm",
        request=dtos.ConfirmVersionDto,
        responses=resources.DocumentResource,
    )
    def post(self, request, tenancy_id, version_id):
        fields = validated(dtos.ConfirmVersionDto, request.data)
        confirmed = services.confirm_document_version(
            tenant=request.user,
            tenancy_id=tenancy_id,
            version_id=version_id,
            idempotency_key=fields["idempotency_key"],
        )
        return Response(resources.DocumentResource(confirmed).data)


class FlagVersionView(TenantView):
    required_permissions = {"POST": "documents.confirm"}

    @extend_schema(
        operation_id="tenant_document_flag",
        request=dtos.FlagVersionDto,
        responses=resources.DocumentResource,
    )
    def post(self, request, tenancy_id, version_id):
        fields = validated(dtos.FlagVersionDto, request.data)
        flagged = services.flag_document_version(
            tenant=request.user,
            tenancy_id=tenancy_id,
            version_id=version_id,
            reason=fields["reason"],
            idempotency_key=fields["idempotency_key"],
        )
        return Response(resources.DocumentResource(flagged).data)


class AdminDocumentsView(PermissionedView):
    required_permissions = {"GET": "documents.admin_view"}

    @extend_schema(
        operation_id="admin_documents_list",
        parameters=[dtos.DocumentListQueryDto],
        responses=resources.DocumentResource(many=True),
    )
    def get(self, request):
        query = validated(dtos.DocumentListQueryDto, request.query_params)
        found = services.list_documents_for_admin(unit_id=query["unit_id"])
        return Response(resources.DocumentResource(found, many=True).data)


class AdminDocumentView(PermissionedView):
    required_permissions = {"GET": "documents.admin_view"}

    @extend_schema(operation_id="admin_document_detail", responses=resources.DocumentResource)
    def get(self, request, document_id):
        found = services.get_document_for_admin(document_id=document_id)
        return Response(resources.DocumentResource(found).data)
