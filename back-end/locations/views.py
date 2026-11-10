from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.security.mfa_permission import MfaCompleted
from locations import dtos, resources, services


class LocationsView(APIView):
    permission_classes = [IsAuthenticated, MfaCompleted]


class StatesView(LocationsView):
    @extend_schema(operation_id="locations_states", responses=resources.StateResource(many=True))
    def get(self, request):
        return Response(resources.StateResource(services.list_states(), many=True).data)


class SuburbsView(LocationsView):
    @extend_schema(
        operation_id="locations_suburbs",
        parameters=[dtos.SuburbQueryDto],
        responses=resources.SuburbResource(many=True),
    )
    def get(self, request):
        query = dtos.SuburbQueryDto(data=request.query_params)
        query.is_valid(raise_exception=True)
        found = services.search_suburbs(**query.validated_data)
        return Response(resources.SuburbResource(found, many=True).data)
