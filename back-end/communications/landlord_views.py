from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from communications import dtos, resources, services
from communications.models import ContactRequestStatus
from properties.landlord_views import IsLandlord
from tenancies.views import validated


class LandlordView(PermissionedView):
    permission_classes = [*PermissionedView.permission_classes, IsLandlord]
    required_permissions = {"GET": "contact_requests.respond", "POST": "contact_requests.respond"}


class LandlordContactRequestsView(LandlordView):
    @extend_schema(
        operation_id="landlord_contact_requests_list",
        parameters=[dtos.ContactRequestQueryDto],
        responses=resources.LandlordContactRequestPageResource,
    )
    def get(self, request):
        query = validated(dtos.ContactRequestQueryDto, request.query_params)
        found = services.list_landlord_contact_requests(
            landlord=request.user, status=query.get("status")
        )
        paginator = PagePagination()
        page = paginator.paginate_queryset(found, request, view=self)
        return paginator.get_paginated_response(
            resources.LandlordContactRequestResource(page, many=True).data
        )


class LandlordContactRequestDetailView(LandlordView):
    @extend_schema(
        operation_id="landlord_contact_requests_get",
        responses=resources.LandlordContactRequestResource,
    )
    def get(self, request, request_id):
        found = services.get_landlord_contact_request(landlord=request.user, request_id=request_id)
        return Response(resources.LandlordContactRequestResource(found).data)


class RespondView(LandlordView):
    new_status: str

    @extend_schema(request=None, responses=resources.LandlordContactRequestResource)
    def post(self, request, request_id):
        found = services.respond_to_contact_request(
            landlord=request.user, request_id=request_id, new_status=self.new_status
        )
        return Response(resources.LandlordContactRequestResource(found).data)


class AcceptContactRequestView(RespondView):
    new_status = ContactRequestStatus.ACCEPTED


class DeclineContactRequestView(RespondView):
    new_status = ContactRequestStatus.DECLINED


class RevokeContactRequestView(RespondView):
    new_status = ContactRequestStatus.REVOKED
