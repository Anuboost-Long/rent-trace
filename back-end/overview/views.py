from drf_spectacular.utils import extend_schema
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.security.mfa_permission import MfaCompleted
from accounts.services.shared.account_rules import is_admin_side
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
