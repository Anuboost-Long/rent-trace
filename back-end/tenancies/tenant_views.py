from drf_spectacular.utils import extend_schema
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from accounts.services.shared.account_rules import has_role
from tenancies import dtos, resources, services
from tenancies.views import validated


class IsTenant(BasePermission):
    message = "Only tenants can use this."

    def has_permission(self, request, view):
        return has_role(request.user, "TENANT")


class TenantView(PermissionedView):
    permission_classes = [*PermissionedView.permission_classes, IsTenant]
    required_permissions = {
        "GET": "tenancies.accept_invitation",
        "POST": "tenancies.accept_invitation",
    }


class MyInvitationsView(TenantView):
    @extend_schema(responses=resources.MyInvitationResource(many=True))
    def get(self, request):
        pending = services.list_my_invitations(user=request.user)
        return Response(resources.MyInvitationResource(pending, many=True).data)


class AcceptByTokenView(TenantView):
    @extend_schema(
        operation_id="tenant_invitations_accept_by_token",
        request=dtos.AcceptInvitationDto,
        responses=resources.MyInvitationResource,
    )
    def post(self, request):
        fields = validated(dtos.AcceptInvitationDto, request.data)
        invitation = services.accept_invitation(user=request.user, token=fields["token"])
        return Response(resources.MyInvitationResource(invitation).data)


class AcceptByIdView(TenantView):
    @extend_schema(
        operation_id="tenant_invitations_accept_by_id",
        request=None,
        responses=resources.MyInvitationResource,
    )
    def post(self, request, invitation_id):
        invitation = services.accept_invitation(user=request.user, invitation_id=invitation_id)
        return Response(resources.MyInvitationResource(invitation).data)
