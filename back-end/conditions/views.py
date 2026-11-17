from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from conditions import dtos, resources, services
from properties.landlord_views import LandlordView


def _validated(dto_class, data):
    serializer = dto_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class ConditionsView(LandlordView):
    required_permissions = {"GET": "conditions.view", "POST": "conditions.submit_baseline"}

    @extend_schema(
        operation_id="landlord_conditions_list",
        parameters=[dtos.ConditionListQueryDto],
        responses=resources.ConditionResource(many=True),
    )
    def get(self, request):
        query = _validated(dtos.ConditionListQueryDto, request.query_params)
        notes = services.list_conditions(landlord=request.user, unit_id=query["unit_id"])
        return Response(resources.ConditionResource(notes, many=True).data)

    @extend_schema(
        operation_id="landlord_conditions_create",
        request=dtos.CreateConditionDto,
        responses={201: resources.ConditionResource},
    )
    def post(self, request):
        fields = _validated(dtos.CreateConditionDto, request.data)
        note = services.create_condition(landlord=request.user, fields=fields)
        return Response(resources.ConditionResource(note).data, status=201)


class ConditionDetailView(LandlordView):
    required_permissions = {
        "PATCH": "conditions.submit_baseline",
        "DELETE": "conditions.submit_baseline",
    }

    @extend_schema(
        operation_id="landlord_conditions_update",
        request=dtos.UpdateConditionDto,
        responses=resources.ConditionResource,
    )
    def patch(self, request, condition_id):
        changes = _validated(dtos.UpdateConditionDto, request.data)
        note = services.update_condition(
            landlord=request.user, condition_id=condition_id, changes=changes
        )
        return Response(resources.ConditionResource(note).data)

    @extend_schema(operation_id="landlord_conditions_delete", responses={204: None})
    def delete(self, request, condition_id):
        services.delete_condition(landlord=request.user, condition_id=condition_id)
        return Response(status=204)
