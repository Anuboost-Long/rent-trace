from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from maintenance import dtos, resources, services
from maintenance.views import _validated


class AdminIssuesView(PermissionedView):
    required_permissions = {"GET": "maintenance.admin_view"}

    @extend_schema(
        operation_id="admin_maintenance_list",
        parameters=[dtos.AdminIssueListQueryDto],
        responses=resources.IssuePageResource,
    )
    def get(self, request):
        query = _validated(dtos.AdminIssueListQueryDto, request.query_params)
        issues = services.list_all_issues(status=query.get("status"), q=query.get("q"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(issues, request, view=self)
        return paginator.get_paginated_response(
            resources.IssueSummaryResource(page, many=True).data
        )


class AdminIssueDetailView(PermissionedView):
    required_permissions = {"GET": "maintenance.admin_view"}

    @extend_schema(operation_id="admin_maintenance_detail", responses=resources.IssueDetailResource)
    def get(self, request, issue_id):
        issue = services.get_any_issue(issue_id=issue_id)
        return Response(resources.IssueDetailResource(issue, context={"user": request.user}).data)
