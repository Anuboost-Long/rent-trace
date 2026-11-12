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


class TenantTenancyView(PermissionedView):
    permission_classes = [*PermissionedView.permission_classes, IsTenant]
    required_permissions = {"GET": "tenancies.view"}


class MyTenanciesView(TenantTenancyView):
    @extend_schema(
        operation_id="tenant_tenancies_list", responses=resources.MyTenancyResource(many=True)
    )
    def get(self, request):
        mine = services.list_my_tenancies(user=request.user)
        return Response(resources.MyTenancyResource(mine, many=True).data)


class MyTenancyDetailView(TenantTenancyView):
    @extend_schema(
        operation_id="tenant_tenancies_retrieve", responses=resources.MyTenancyDetailResource
    )
    def get(self, request, tenancy_id):
        found = services.get_my_tenancy(user=request.user, tenancy_id=tenancy_id)
        return Response(resources.MyTenancyDetailResource(found).data)


class RequestHousemateView(TenantTenancyView):
    required_permissions = {"POST": "tenancies.invite_housemate"}

    @extend_schema(
        operation_id="tenant_tenancies_request_housemate",
        request=dtos.RequestHousemateDto,
        responses={201: resources.HousemateRequestResource},
    )
    def post(self, request, tenancy_id):
        fields = validated(dtos.RequestHousemateDto, request.data)
        invitation = services.request_housemate(
            user=request.user, tenancy_id=tenancy_id, email=fields["email"]
        )
        return Response(resources.HousemateRequestResource(invitation).data, status=201)


class WithdrawHousemateView(TenantTenancyView):
    required_permissions = {"POST": "tenancies.invite_housemate"}

    @extend_schema(
        operation_id="tenant_tenancies_withdraw_housemate",
        request=None,
        responses=resources.HousemateRequestResource,
    )
    def post(self, request, tenancy_id, invitation_id):
        invitation = services.withdraw_housemate(
            user=request.user, tenancy_id=tenancy_id, invitation_id=invitation_id
        )
        return Response(resources.HousemateRequestResource(invitation).data)


class ApproveTermChangeView(TenantTenancyView):
    required_permissions = {"POST": "tenancies.approve_terms"}

    @extend_schema(
        operation_id="tenant_tenancies_approve_terms",
        request=None,
        responses=resources.MyTenancyDetailResource,
    )
    def post(self, request, tenancy_id, change_id):
        services.respond_to_term_change(
            user=request.user, tenancy_id=tenancy_id, change_id=change_id, decision="APPROVED"
        )
        mine = services.get_my_tenancy(user=request.user, tenancy_id=tenancy_id)
        return Response(resources.MyTenancyDetailResource(mine).data)


class DeclineTermChangeView(TenantTenancyView):
    required_permissions = {"POST": "tenancies.approve_terms"}

    @extend_schema(
        operation_id="tenant_tenancies_decline_terms",
        request=None,
        responses=resources.MyTenancyDetailResource,
    )
    def post(self, request, tenancy_id, change_id):
        services.respond_to_term_change(
            user=request.user, tenancy_id=tenancy_id, change_id=change_id, decision="DECLINED"
        )
        mine = services.get_my_tenancy(user=request.user, tenancy_id=tenancy_id)
        return Response(resources.MyTenancyDetailResource(mine).data)
