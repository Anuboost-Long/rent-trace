from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from accounts.security.super_admin_permission import IsSuperAdmin
from reviews import dtos, resources, services
from tenancies.views import validated


class AdminEvidenceView(PermissionedView):
    required_permissions = {"GET": "reviews.admin_review"}

    @extend_schema(
        operation_id="admin_condition_evidence_list",
        parameters=[dtos.EvidenceListQueryDto],
        responses=resources.EvidenceResource(many=True),
    )
    def get(self, request):
        query = validated(dtos.EvidenceListQueryDto, request.query_params)
        found = services.list_evidence_for_admin(unit_id=query["unit_id"])
        return Response(resources.EvidenceResource(found, many=True).data)


class SuperAdminEvidenceView(PermissionedView):
    """A super admin does a party's action; the history shows who they acted for."""

    permission_classes = [*PermissionedView.permission_classes, IsSuperAdmin]


class ApproveForLandlordView(SuperAdminEvidenceView):
    required_permissions = {"POST": "reviews.decide"}

    @extend_schema(
        operation_id="admin_condition_evidence_approve",
        request=dtos.ApproveEvidenceDto,
        responses=resources.EvidenceResource,
    )
    def post(self, request, request_id):
        fields = validated(dtos.ApproveEvidenceDto, request.data)
        approved = services.approve_evidence(
            user=request.user,
            request_id=request_id,
            idempotency_key=fields["idempotency_key"],
            as_admin=True,
        )
        return Response(resources.EvidenceResource(approved).data)


class RejectForLandlordView(SuperAdminEvidenceView):
    required_permissions = {"POST": "reviews.decide"}

    @extend_schema(
        operation_id="admin_condition_evidence_reject",
        request=dtos.RejectEvidenceDto,
        responses=resources.EvidenceResource,
    )
    def post(self, request, request_id):
        fields = validated(dtos.RejectEvidenceDto, request.data)
        rejected = services.reject_evidence(
            user=request.user,
            request_id=request_id,
            reason=fields["reason"],
            idempotency_key=fields["idempotency_key"],
            as_admin=True,
        )
        return Response(resources.EvidenceResource(rejected).data)


class RequestInformationForLandlordView(SuperAdminEvidenceView):
    required_permissions = {"POST": "reviews.decide"}

    @extend_schema(
        operation_id="admin_condition_evidence_request_information",
        request=dtos.RequestInformationDto,
        responses=resources.EvidenceResource,
    )
    def post(self, request, request_id):
        fields = validated(dtos.RequestInformationDto, request.data)
        asked = services.request_information(
            user=request.user,
            request_id=request_id,
            reason=fields["reason"],
            idempotency_key=fields["idempotency_key"],
            as_admin=True,
        )
        return Response(resources.EvidenceResource(asked).data)


class CancelForTenantView(SuperAdminEvidenceView):
    required_permissions = {"POST": "reviews.submit"}

    @extend_schema(
        operation_id="admin_condition_evidence_cancel",
        request=None,
        responses=resources.EvidenceResource,
    )
    def post(self, request, request_id):
        cancelled = services.cancel_evidence(
            user=request.user, request_id=request_id, as_admin=True
        )
        return Response(resources.EvidenceResource(cancelled).data)


class RespondForTenantView(SuperAdminEvidenceView):
    required_permissions = {"POST": "reviews.submit"}

    @extend_schema(
        operation_id="admin_condition_evidence_respond",
        request=dtos.RespondToInformationDto,
        responses=resources.EvidenceResource,
    )
    def post(self, request, request_id):
        fields = validated(dtos.RespondToInformationDto, request.data)
        answered = services.respond_to_information(
            user=request.user,
            request_id=request_id,
            message=fields.pop("message"),
            changes=fields,
            as_admin=True,
        )
        return Response(resources.EvidenceResource(answered).data)
