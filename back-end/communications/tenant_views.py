from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from communications import dtos, resources, services
from tenancies.tenant_views import IsTenant
from tenancies.views import validated


class TenantView(PermissionedView):
    permission_classes = [*PermissionedView.permission_classes, IsTenant]
    required_permissions = {"GET": "contact_requests.send", "POST": "contact_requests.send"}


class ContactRequestsView(TenantView):
    @extend_schema(
        operation_id="tenant_contact_requests_list",
        parameters=[dtos.ContactRequestQueryDto],
        responses=resources.TenantContactRequestPageResource,
    )
    def get(self, request):
        query = validated(dtos.ContactRequestQueryDto, request.query_params)
        found = services.list_my_contact_requests(tenant=request.user, status=query.get("status"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(found, request, view=self)
        return paginator.get_paginated_response(
            resources.TenantContactRequestResource(page, many=True).data
        )

    @extend_schema(
        request=dtos.CreateContactRequestDto,
        responses={201: resources.TenantContactRequestResource},
    )
    def post(self, request):
        fields = validated(dtos.CreateContactRequestDto, request.data)
        created = services.create_contact_request(tenant=request.user, fields=fields)
        return Response(resources.TenantContactRequestResource(created).data, status=201)


class ContactRequestDetailView(TenantView):
    @extend_schema(
        operation_id="tenant_contact_requests_get", responses=resources.TenantContactRequestResource
    )
    def get(self, request, request_id):
        found = services.get_my_contact_request(tenant=request.user, request_id=request_id)
        return Response(resources.TenantContactRequestResource(found).data)


class CancelContactRequestView(TenantView):
    @extend_schema(request=None, responses=resources.TenantContactRequestResource)
    def post(self, request, request_id):
        found = services.cancel_contact_request(tenant=request.user, request_id=request_id)
        return Response(resources.TenantContactRequestResource(found).data)
