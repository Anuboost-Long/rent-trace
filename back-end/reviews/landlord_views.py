from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from properties.landlord_views import LandlordView
from reviews import dtos, resources, services
from tenancies.views import validated


class UnitEvidenceView(LandlordView):
    required_permissions = {"GET": "reviews.view"}

    @extend_schema(
        operation_id="landlord_condition_evidence_list",
        parameters=[dtos.EvidenceListQueryDto],
        responses=resources.EvidenceResource(many=True),
    )
    def get(self, request):
        query = validated(dtos.EvidenceListQueryDto, request.query_params)
        found = services.list_evidence_for_unit(landlord=request.user, unit_id=query["unit_id"])
        return Response(resources.EvidenceResource(found, many=True).data)


class ApproveEvidenceView(LandlordView):
    required_permissions = {"POST": "reviews.decide"}

    @extend_schema(
        operation_id="landlord_condition_evidence_approve",
        request=dtos.ApproveEvidenceDto,
        responses=resources.EvidenceResource,
    )
    def post(self, request, request_id):
        fields = validated(dtos.ApproveEvidenceDto, request.data)
        approved = services.approve_evidence(
            user=request.user,
            request_id=request_id,
            idempotency_key=fields["idempotency_key"],
        )
        return Response(resources.EvidenceResource(approved).data)


class RejectEvidenceView(LandlordView):
    required_permissions = {"POST": "reviews.decide"}

    @extend_schema(
        operation_id="landlord_condition_evidence_reject",
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
        )
        return Response(resources.EvidenceResource(rejected).data)


class EscalateEvidenceView(LandlordView):
    required_permissions = {"POST": "reviews.escalate"}

    @extend_schema(
        operation_id="landlord_condition_evidence_escalate",
        request=dtos.EscalateEvidenceDto,
        responses=resources.EvidenceResource,
    )
    def post(self, request, request_id):
        fields = validated(dtos.EscalateEvidenceDto, request.data)
        escalated = services.escalate_evidence(
            user=request.user, request_id=request_id, reason=fields["reason"]
        )
        return Response(resources.EvidenceResource(escalated).data)
