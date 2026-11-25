from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from reviews import dtos, resources, services
from tenancies.tenant_views import TenantView
from tenancies.views import validated


class MyEvidenceView(TenantView):
    required_permissions = {"GET": "reviews.view", "POST": "reviews.submit"}

    @extend_schema(
        operation_id="tenant_condition_evidence_list",
        responses=resources.EvidenceResource(many=True),
    )
    def get(self, request, tenancy_id):
        mine = services.list_my_evidence(tenant=request.user, tenancy_id=tenancy_id)
        return Response(resources.EvidenceResource(mine, many=True).data)

    @extend_schema(
        operation_id="tenant_condition_evidence_submit",
        request=dtos.SubmitEvidenceDto,
        responses={201: resources.EvidenceResource},
    )
    def post(self, request, tenancy_id):
        fields = validated(dtos.SubmitEvidenceDto, request.data)
        submitted = services.submit_condition_evidence(
            user=request.user, tenancy_id=tenancy_id, fields=fields
        )
        return Response(resources.EvidenceResource(submitted).data, status=201)


class CancelEvidenceView(TenantView):
    required_permissions = {"POST": "reviews.submit"}

    @extend_schema(
        operation_id="tenant_condition_evidence_cancel",
        request=None,
        responses=resources.EvidenceResource,
    )
    def post(self, request, tenancy_id, request_id):
        cancelled = services.cancel_evidence(user=request.user, request_id=request_id)
        return Response(resources.EvidenceResource(cancelled).data)
