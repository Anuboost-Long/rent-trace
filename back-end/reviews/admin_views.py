from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from reviews import dtos, resources, services
from reviews.models import ReviewRequest
from tenancies.views import validated


class ReviewCasesView(PermissionedView):
    required_permissions = {"GET": "reviews.admin_review"}

    @extend_schema(
        operation_id="admin_review_cases_list",
        parameters=[dtos.CaseListQueryDto],
        responses=resources.CasePageResource,
    )
    def get(self, request):
        query = validated(dtos.CaseListQueryDto, request.query_params)
        cases = services.list_review_cases(status=query.get("status"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(cases, request, view=self)
        return paginator.get_paginated_response(resources.CaseResource(page, many=True).data)


def _answered(case):
    detailed = ReviewRequest.objects.with_case_details().get(pk=case.pk)
    return Response(resources.CaseResource(detailed).data)


class ApproveCaseView(PermissionedView):
    required_permissions = {"POST": "reviews.admin_review"}

    @extend_schema(
        operation_id="admin_review_case_approve",
        request=dtos.DecideCaseDto,
        responses=resources.CaseResource,
    )
    def post(self, request, case_id):
        fields = validated(dtos.DecideCaseDto, request.data)
        case = services.approve_dispute(
            admin=request.user,
            case_id=case_id,
            reason=fields["reason"],
            idempotency_key=fields["idempotency_key"],
        )
        return _answered(case)


class RejectCaseView(PermissionedView):
    required_permissions = {"POST": "reviews.admin_review"}

    @extend_schema(
        operation_id="admin_review_case_reject",
        request=dtos.DecideCaseDto,
        responses=resources.CaseResource,
    )
    def post(self, request, case_id):
        fields = validated(dtos.DecideCaseDto, request.data)
        case = services.reject_dispute(
            admin=request.user,
            case_id=case_id,
            reason=fields["reason"],
            idempotency_key=fields["idempotency_key"],
        )
        return _answered(case)
