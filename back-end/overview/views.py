from drf_spectacular.utils import extend_schema
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.security.mfa_permission import MfaCompleted
from accounts.services.shared.account_rules import has_role, is_admin_side
from overview import resources, services


class IsAdminSide(BasePermission):
    message = "Only admins can use this."

    def has_permission(self, request, view):
        return is_admin_side(request.user)


class OverviewView(APIView):
    permission_classes = [IsAuthenticated, MfaCompleted, IsAdminSide]

    @extend_schema(responses=resources.OverviewResource)
    def get(self, request):
        return Response(resources.OverviewResource(services.get_overview(user=request.user)).data)


class IsLandlord(BasePermission):
    message = "Only landlords can use this."

    def has_permission(self, request, view):
        return has_role(request.user, "LANDLORD")


class LandlordOverviewView(APIView):
    permission_classes = [IsAuthenticated, MfaCompleted, IsLandlord]

    @extend_schema(operation_id="landlord_overview", responses=resources.OverviewResource)
    def get(self, request):
        return Response(
            resources.OverviewResource(services.get_landlord_overview(user=request.user)).data
        )
