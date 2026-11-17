from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from communications import dtos, resources, services
from tenancies.views import validated


class AdminView(PermissionedView):
    required_permissions = {"GET": "contact_requests.admin_view"}


class AdminContactRequestsView(AdminView):
    @extend_schema(
        operation_id="admin_contact_requests_list",
        parameters=[dtos.AdminContactRequestQueryDto],
        responses=resources.AdminContactRequestPageResource,
    )
    def get(self, request):
        query = validated(dtos.AdminContactRequestQueryDto, request.query_params)
        found = services.list_all_contact_requests(status=query.get("status"), q=query.get("q"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(found, request, view=self)
        return paginator.get_paginated_response(
            resources.AdminContactRequestResource(page, many=True).data
        )


class AdminContactRequestDetailView(AdminView):
    @extend_schema(
        operation_id="admin_contact_requests_get",
        responses=resources.AdminContactRequestResource,
    )
    def get(self, request, request_id):
        found = services.get_any_contact_request(request_id=request_id)
        return Response(resources.AdminContactRequestResource(found).data)
