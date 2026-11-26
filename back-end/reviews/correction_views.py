from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from properties.landlord_views import LandlordView
from reviews import dtos, resources, services
from tenancies.tenant_views import TenantView
from tenancies.views import validated


class TenantCorrectionsView(TenantView):
    required_permissions = {"GET": "reviews.view", "POST": "reviews.submit"}

    @extend_schema(
        operation_id="tenant_condition_corrections_list",
        responses=resources.CorrectionResource(many=True),
    )
    def get(self, request, tenancy_id):
        mine = services.list_corrections_for_tenancy(tenant=request.user, tenancy_id=tenancy_id)
        return Response(resources.CorrectionResource(mine, many=True).data)

    @extend_schema(
        operation_id="tenant_condition_correction_request",
        request=dtos.RequestCorrectionDto,
        responses={201: resources.CorrectionResource},
    )
    def post(self, request, tenancy_id):
        fields = validated(dtos.RequestCorrectionDto, request.data)
        asked = services.request_correction(
            user=request.user,
            record_id=fields.pop("record_id"),
            fields=fields,
            tenancy_id=tenancy_id,
        )
        return Response(resources.CorrectionResource(asked).data, status=201)


class CancelTenantCorrectionView(TenantView):
    required_permissions = {"POST": "reviews.submit"}

    @extend_schema(
        operation_id="tenant_condition_correction_cancel",
        request=None,
        responses=resources.CorrectionResource,
    )
    def post(self, request, tenancy_id, request_id):
        cancelled = services.cancel_correction(user=request.user, request_id=request_id)
        return Response(resources.CorrectionResource(cancelled).data)


class LandlordCorrectionsView(LandlordView):
    required_permissions = {"GET": "reviews.view", "POST": "reviews.submit"}

    @extend_schema(
        operation_id="landlord_condition_corrections_list",
        parameters=[dtos.UnitCorrectionsQueryDto],
        responses=resources.CorrectionResource(many=True),
    )
    def get(self, request):
        query = validated(dtos.UnitCorrectionsQueryDto, request.query_params)
        found = services.list_corrections_for_unit(landlord=request.user, unit_id=query["unit_id"])
        return Response(resources.CorrectionResource(found, many=True).data)

    @extend_schema(
        operation_id="landlord_condition_correction_request",
        request=dtos.RequestCorrectionDto,
        responses={201: resources.CorrectionResource},
    )
    def post(self, request):
        fields = validated(dtos.RequestCorrectionDto, request.data)
        asked = services.request_correction(
            user=request.user, record_id=fields.pop("record_id"), fields=fields
        )
        return Response(resources.CorrectionResource(asked).data, status=201)


class CancelLandlordCorrectionView(LandlordView):
    required_permissions = {"POST": "reviews.submit"}

    @extend_schema(
        operation_id="landlord_condition_correction_cancel",
        request=None,
        responses=resources.CorrectionResource,
    )
    def post(self, request, request_id):
        cancelled = services.cancel_correction(user=request.user, request_id=request_id)
        return Response(resources.CorrectionResource(cancelled).data)


class AdminCorrectionsView(PermissionedView):
    required_permissions = {"GET": "reviews.admin_review"}

    @extend_schema(
        operation_id="admin_condition_corrections_list",
        parameters=[dtos.CorrectionListQueryDto],
        responses=resources.CorrectionPageResource,
    )
    def get(self, request):
        query = validated(dtos.CorrectionListQueryDto, request.query_params)
        queue = services.list_correction_queue(status=query.get("status"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(queue, request, view=self)
        return paginator.get_paginated_response(resources.CorrectionResource(page, many=True).data)


class DecideCorrectionView(PermissionedView):
    required_permissions = {"POST": "reviews.admin_review"}

    def decide(self, request, request_id, service):
        fields = validated(dtos.DecideCaseDto, request.data)
        decided = service(
            admin=request.user,
            request_id=request_id,
            reason=fields["reason"],
            idempotency_key=fields["idempotency_key"],
        )
        return Response(resources.CorrectionResource(decided).data)


class ApproveCorrectionView(DecideCorrectionView):
    @extend_schema(
        operation_id="admin_condition_correction_approve",
        request=dtos.DecideCaseDto,
        responses=resources.CorrectionResource,
    )
    def post(self, request, request_id):
        return self.decide(request, request_id, services.approve_correction)


class RejectCorrectionView(DecideCorrectionView):
    @extend_schema(
        operation_id="admin_condition_correction_reject",
        request=dtos.DecideCaseDto,
        responses=resources.CorrectionResource,
    )
    def post(self, request, request_id):
        return self.decide(request, request_id, services.reject_correction)
