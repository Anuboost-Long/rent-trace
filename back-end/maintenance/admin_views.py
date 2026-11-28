from django.http import FileResponse
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from accounts.security.super_admin_permission import IsSuperAdmin
from common.pagination import PagePagination
from maintenance import dtos, resources, services
from maintenance.models import ClosureDecision
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


def _detail(request, issue_id):
    issue = services.get_any_issue(issue_id=issue_id)
    return Response(resources.IssueDetailResource(issue, context={"user": request.user}).data)


class AdminIssueDetailView(PermissionedView):
    required_permissions = {"GET": "maintenance.admin_view"}

    @extend_schema(operation_id="admin_maintenance_detail", responses=resources.IssueDetailResource)
    def get(self, request, issue_id):
        return _detail(request, issue_id)


class AdminIssuePhotoView(PermissionedView):
    required_permissions = {"GET": "maintenance.admin_view"}

    @extend_schema(
        operation_id="admin_maintenance_photo_file",
        responses={(200, "application/octet-stream"): bytes},
    )
    def get(self, request, issue_id, file_id):
        stored, content = services.open_issue_photo(
            user=request.user, issue_id=issue_id, file_id=file_id, as_admin=True
        )
        response = FileResponse(
            content, content_type=stored.mime_type, filename=stored.original_name
        )
        response["Cache-Control"] = "private, max-age=3600"
        return response


class SuperAdminActionView(PermissionedView):
    """A super admin does a landlord's status move for the property's primary owner."""

    permission_classes = [*PermissionedView.permission_classes, IsSuperAdmin]


class AdminAcknowledgeIssueView(SuperAdminActionView):
    required_permissions = {"POST": "maintenance.confirm_start"}

    @extend_schema(
        operation_id="admin_maintenance_acknowledge",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        services.acknowledge_issue(user=request.user, issue_id=issue_id, as_admin=True)
        return _detail(request, issue_id)


class AdminStartWorkView(SuperAdminActionView):
    required_permissions = {"POST": "maintenance.confirm_start"}

    @extend_schema(
        operation_id="admin_maintenance_start",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        services.start_work(user=request.user, issue_id=issue_id, as_admin=True)
        return _detail(request, issue_id)


class AdminCloseVacantView(SuperAdminActionView):
    required_permissions = {"POST": "maintenance.close_vacant"}

    @extend_schema(
        operation_id="admin_maintenance_close_vacant",
        request=dtos.ClosureDto,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        fields = _validated(dtos.ClosureDto, request.data)
        services.close_vacant(user=request.user, issue_id=issue_id, as_admin=True, **fields)
        return _detail(request, issue_id)


class AdminProposeClosureView(SuperAdminActionView):
    required_permissions = {"POST": "maintenance.propose_closure"}

    @extend_schema(
        operation_id="admin_maintenance_propose_closure",
        request=dtos.ClosureDto,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        fields = _validated(dtos.ClosureDto, request.data)
        services.propose_closure(user=request.user, issue_id=issue_id, as_admin=True, **fields)
        return _detail(request, issue_id)


class AdminWithdrawClosureView(SuperAdminActionView):
    required_permissions = {"POST": "maintenance.propose_closure"}

    @extend_schema(
        operation_id="admin_maintenance_withdraw_closure",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        services.withdraw_closure(user=request.user, issue_id=issue_id, as_admin=True)
        return _detail(request, issue_id)


class AdminApproveClosureView(SuperAdminActionView):
    required_permissions = {"POST": "maintenance.review_closure"}
    decision = ClosureDecision.APPROVED

    @extend_schema(
        operation_id="admin_maintenance_approve_closure",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id, proposal_id):
        services.respond_to_closure(
            user=request.user,
            issue_id=issue_id,
            proposal_id=proposal_id,
            decision=self.decision,
            as_admin=True,
        )
        return _detail(request, issue_id)


class AdminRejectClosureView(AdminApproveClosureView):
    decision = ClosureDecision.REJECTED

    @extend_schema(
        operation_id="admin_maintenance_reject_closure",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id, proposal_id):
        return super().post(request, issue_id, proposal_id)


class AdminAssignProviderView(SuperAdminActionView):
    required_permissions = {"POST": "maintenance.confirm_start"}

    @extend_schema(
        operation_id="admin_maintenance_assign_provider",
        request=dtos.AssignProviderDto,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        fields = _validated(dtos.AssignProviderDto, request.data)
        services.assign_provider(user=request.user, issue_id=issue_id, as_admin=True, **fields)
        return _detail(request, issue_id)


class AdminCompleteVisitView(SuperAdminActionView):
    required_permissions = {"POST": "maintenance.confirm_start"}

    @extend_schema(
        operation_id="admin_maintenance_complete_visit",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        services.complete_visit(user=request.user, issue_id=issue_id, as_admin=True)
        return _detail(request, issue_id)
