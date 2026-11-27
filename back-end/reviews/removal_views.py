from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from properties.landlord_views import LandlordView
from reviews import dtos, resources, services
from tenancies.tenant_views import TenantView
from tenancies.views import validated


class TenantRemovalsView(TenantView):
    required_permissions = {"GET": "reviews.view", "POST": "reviews.request_removal"}

    @extend_schema(
        operation_id="tenant_removal_requests_list",
        responses=resources.RemovalResource(many=True),
    )
    def get(self, request, tenancy_id):
        mine = services.list_removals_for_tenancy(tenant=request.user, tenancy_id=tenancy_id)
        return Response(resources.RemovalResource(mine, many=True).data)

    @extend_schema(
        operation_id="tenant_removal_request_create",
        request=dtos.RequestRemovalDto,
        responses={201: resources.RemovalResource},
    )
    def post(self, request, tenancy_id):
        fields = validated(dtos.RequestRemovalDto, request.data)
        asked = services.request_removal(
            user=request.user,
            record_ids=fields["record_ids"],
            reason=fields["reason"],
            include_descendants=fields["include_descendants"],
            tenancy_id=tenancy_id,
        )
        return Response(resources.RemovalResource(asked).data, status=201)


class CancelTenantRemovalView(TenantView):
    required_permissions = {"POST": "reviews.request_removal"}

    @extend_schema(
        operation_id="tenant_removal_request_cancel",
        request=None,
        responses=resources.RemovalResource,
    )
    def post(self, request, tenancy_id, request_id):
        cancelled = services.cancel_removal(user=request.user, request_id=request_id)
        return Response(resources.RemovalResource(cancelled).data)


class LandlordRemovalsView(LandlordView):
    required_permissions = {"GET": "reviews.view", "POST": "reviews.request_removal"}

    @extend_schema(
        operation_id="landlord_removal_requests_list",
        parameters=[dtos.UnitCorrectionsQueryDto],
        responses=resources.RemovalResource(many=True),
    )
    def get(self, request):
        query = validated(dtos.UnitCorrectionsQueryDto, request.query_params)
        found = services.list_removals_for_unit(landlord=request.user, unit_id=query["unit_id"])
        return Response(resources.RemovalResource(found, many=True).data)

    @extend_schema(
        operation_id="landlord_removal_request_create",
        request=dtos.RequestRemovalDto,
        responses={201: resources.RemovalResource},
    )
    def post(self, request):
        fields = validated(dtos.RequestRemovalDto, request.data)
        asked = services.request_removal(
            user=request.user,
            record_ids=fields["record_ids"],
            reason=fields["reason"],
            include_descendants=fields["include_descendants"],
        )
        return Response(resources.RemovalResource(asked).data, status=201)


class CancelLandlordRemovalView(LandlordView):
    required_permissions = {"POST": "reviews.request_removal"}

    @extend_schema(
        operation_id="landlord_removal_request_cancel",
        request=None,
        responses=resources.RemovalResource,
    )
    def post(self, request, request_id):
        cancelled = services.cancel_removal(user=request.user, request_id=request_id)
        return Response(resources.RemovalResource(cancelled).data)


class AdminRemovalsView(PermissionedView):
    required_permissions = {"GET": "reviews.review_removal"}

    @extend_schema(
        operation_id="admin_removal_requests_list",
        parameters=[dtos.RemovalListQueryDto],
        responses=resources.RemovalPageResource,
    )
    def get(self, request):
        query = validated(dtos.RemovalListQueryDto, request.query_params)
        queue = services.list_removal_queue(status=query.get("status"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(queue, request, view=self)
        return paginator.get_paginated_response(resources.RemovalResource(page, many=True).data)


class DecideRemovalView(PermissionedView):
    required_permissions = {"POST": "reviews.review_removal"}

    def decide(self, request, request_id, service):
        fields = validated(dtos.DecideCaseDto, request.data)
        decided = service(
            admin=request.user,
            request_id=request_id,
            reason=fields["reason"],
            idempotency_key=fields["idempotency_key"],
        )
        return Response(resources.RemovalResource(decided).data)


class ApproveRemovalView(DecideRemovalView):
    @extend_schema(
        operation_id="admin_removal_request_approve",
        request=dtos.DecideCaseDto,
        responses=resources.RemovalResource,
    )
    def post(self, request, request_id):
        return self.decide(request, request_id, services.approve_removal)


class RejectRemovalView(DecideRemovalView):
    @extend_schema(
        operation_id="admin_removal_request_reject",
        request=dtos.DecideCaseDto,
        responses=resources.RemovalResource,
    )
    def post(self, request, request_id):
        return self.decide(request, request_id, services.reject_removal)
