from drf_spectacular.utils import extend_schema
from rest_framework.permissions import BasePermission

from accounts.security.permissioned_view import PermissionedView
from accounts.services.shared.account_rules import has_role
from tenancies import dtos, resources, views


class IsLandlord(BasePermission):
    message = "Only landlords can use this."

    def has_permission(self, request, view):
        return has_role(request.user, "LANDLORD")


class LandlordScope(views.TenancyScope):
    permission_classes = [*PermissionedView.permission_classes, IsLandlord]

    def owned_by(self, request):
        return request.user


class LandlordTenanciesView(LandlordScope, views.TenanciesView):
    required_permissions = {"GET": "tenancies.view", "POST": "tenancies.create"}

    @extend_schema(
        operation_id="landlord_tenancies_list",
        parameters=[dtos.TenancyListQueryDto],
        responses=resources.TenancyPageResource,
    )
    def get(self, request):
        return super().get(request)


class LandlordTenancyDetailView(LandlordScope, views.TenancyDetailView):
    required_permissions = {"GET": "tenancies.view"}


class LandlordInvitationsView(LandlordScope, views.InvitationsView):
    required_permissions = {"POST": "tenancies.manage_parties"}


class LandlordResendInvitationView(LandlordScope, views.ResendInvitationView):
    required_permissions = {"POST": "tenancies.manage_parties"}


class LandlordRevokeInvitationView(LandlordScope, views.RevokeInvitationView):
    required_permissions = {"POST": "tenancies.manage_parties"}


class LandlordActivateTenancyView(LandlordScope, views.ActivateTenancyView):
    required_permissions = {"POST": "tenancies.update"}

    @extend_schema(
        operation_id="landlord_tenancies_activate",
        request=None,
        responses=resources.TenancyDetailResource,
    )
    def post(self, request, tenancy_id):
        return super().post(request, tenancy_id)


class LandlordEndTenancyView(LandlordScope, views.EndTenancyView):
    required_permissions = {"POST": "tenancies.update"}

    @extend_schema(
        operation_id="landlord_tenancies_end",
        request=None,
        responses=resources.TenancyDetailResource,
    )
    def post(self, request, tenancy_id):
        return super().post(request, tenancy_id)


class LandlordCancelTenancyView(LandlordScope, views.CancelTenancyView):
    required_permissions = {"POST": "tenancies.update"}

    @extend_schema(
        operation_id="landlord_tenancies_cancel",
        request=None,
        responses=resources.TenancyDetailResource,
    )
    def post(self, request, tenancy_id):
        return super().post(request, tenancy_id)


class LandlordApproveHousemateView(LandlordScope, views.ApproveHousemateView):
    required_permissions = {"POST": "tenancies.manage_parties"}

    @extend_schema(
        operation_id="landlord_tenancies_approve_housemate",
        request=None,
        responses=resources.InvitationResource,
    )
    def post(self, request, tenancy_id, invitation_id):
        return super().post(request, tenancy_id, invitation_id)


class LandlordDeclineHousemateView(LandlordScope, views.DeclineHousemateView):
    required_permissions = {"POST": "tenancies.manage_parties"}

    @extend_schema(
        operation_id="landlord_tenancies_decline_housemate",
        request=None,
        responses=resources.InvitationResource,
    )
    def post(self, request, tenancy_id, invitation_id):
        return super().post(request, tenancy_id, invitation_id)
