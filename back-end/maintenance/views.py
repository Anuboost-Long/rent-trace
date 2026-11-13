from drf_spectacular.utils import extend_schema
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from accounts.services.shared.account_rules import has_role
from common.pagination import PagePagination
from maintenance import dtos, resources, services
from maintenance.models import ClosureDecision
from providers import services as providers_services
from providers.resources import ServiceCategoryResource


def _validated(dto_class, data):
    serializer = dto_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class IsLandlordOrTenant(BasePermission):
    message = "Only tenants and landlords can use maintenance."

    def has_permission(self, request, view):
        return has_role(request.user, "TENANT") or has_role(request.user, "LANDLORD")


def _detail(request, issue_id):
    issue = services.get_issue(user=request.user, issue_id=issue_id)
    return Response(resources.IssueDetailResource(issue, context={"user": request.user}).data)


class MaintenanceView(PermissionedView):
    permission_classes = [*PermissionedView.permission_classes, IsLandlordOrTenant]


class IssueCategoriesView(MaintenanceView):
    required_permissions = {"GET": "maintenance.view"}

    @extend_schema(
        operation_id="maintenance_categories_list",
        responses=ServiceCategoryResource(many=True),
    )
    def get(self, request):
        return Response(
            ServiceCategoryResource(providers_services.list_categories(), many=True).data
        )


class IssuesView(MaintenanceView):
    required_permissions = {"GET": "maintenance.view", "POST": "maintenance.report"}

    @extend_schema(
        operation_id="maintenance_list",
        parameters=[dtos.IssueListQueryDto],
        responses=resources.IssuePageResource,
    )
    def get(self, request):
        query = _validated(dtos.IssueListQueryDto, request.query_params)
        issues = services.list_issues(user=request.user, status=query.get("status"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(issues, request, view=self)
        return paginator.get_paginated_response(
            resources.IssueSummaryResource(page, many=True).data
        )

    @extend_schema(
        operation_id="maintenance_report",
        request=dtos.ReportIssueDto,
        responses={201: resources.IssueDetailResource},
    )
    def post(self, request):
        fields = _validated(dtos.ReportIssueDto, request.data)
        issue = services.report_issue(user=request.user, fields=fields)
        response = _detail(request, issue.pk)
        response.status_code = 201
        return response


class IssueDetailView(MaintenanceView):
    required_permissions = {"GET": "maintenance.view"}

    @extend_schema(operation_id="maintenance_detail", responses=resources.IssueDetailResource)
    def get(self, request, issue_id):
        return _detail(request, issue_id)


class AcknowledgeIssueView(MaintenanceView):
    required_permissions = {"POST": "maintenance.confirm_start"}

    @extend_schema(
        operation_id="maintenance_acknowledge",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        services.acknowledge_issue(user=request.user, issue_id=issue_id)
        return _detail(request, issue_id)


class StartWorkView(MaintenanceView):
    required_permissions = {"POST": "maintenance.confirm_start"}

    @extend_schema(
        operation_id="maintenance_start", request=None, responses=resources.IssueDetailResource
    )
    def post(self, request, issue_id):
        services.start_work(user=request.user, issue_id=issue_id)
        return _detail(request, issue_id)


class AssignProviderView(MaintenanceView):
    required_permissions = {"POST": "maintenance.confirm_start"}

    @extend_schema(
        operation_id="maintenance_assign_provider",
        request=dtos.AssignProviderDto,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        fields = _validated(dtos.AssignProviderDto, request.data)
        services.assign_provider(user=request.user, issue_id=issue_id, **fields)
        return _detail(request, issue_id)


class CompleteVisitView(MaintenanceView):
    required_permissions = {"POST": "maintenance.confirm_start"}

    @extend_schema(
        operation_id="maintenance_complete_visit",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        services.complete_visit(user=request.user, issue_id=issue_id)
        return _detail(request, issue_id)


class ProposeClosureView(MaintenanceView):
    required_permissions = {"POST": "maintenance.propose_closure"}

    @extend_schema(
        operation_id="maintenance_propose_closure",
        request=dtos.ClosureDto,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        fields = _validated(dtos.ClosureDto, request.data)
        services.propose_closure(user=request.user, issue_id=issue_id, **fields)
        return _detail(request, issue_id)


class WithdrawClosureView(MaintenanceView):
    required_permissions = {"POST": "maintenance.propose_closure"}

    @extend_schema(
        operation_id="maintenance_withdraw_closure",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        services.withdraw_closure(user=request.user, issue_id=issue_id)
        return _detail(request, issue_id)


class ApproveClosureView(MaintenanceView):
    required_permissions = {"POST": "maintenance.review_closure"}
    decision = ClosureDecision.APPROVED

    @extend_schema(
        operation_id="maintenance_approve_closure",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id, proposal_id):
        services.respond_to_closure(
            user=request.user, issue_id=issue_id, proposal_id=proposal_id, decision=self.decision
        )
        return _detail(request, issue_id)


class RejectClosureView(ApproveClosureView):
    decision = ClosureDecision.REJECTED

    @extend_schema(
        operation_id="maintenance_reject_closure",
        request=None,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id, proposal_id):
        return super().post(request, issue_id, proposal_id)


class CloseVacantView(MaintenanceView):
    required_permissions = {"POST": "maintenance.close_vacant"}

    @extend_schema(
        operation_id="maintenance_close_vacant",
        request=dtos.ClosureDto,
        responses=resources.IssueDetailResource,
    )
    def post(self, request, issue_id):
        fields = _validated(dtos.ClosureDto, request.data)
        services.close_vacant(user=request.user, issue_id=issue_id, **fields)
        return _detail(request, issue_id)
