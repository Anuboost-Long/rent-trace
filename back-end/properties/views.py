from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from properties import dtos, resources, services


def _validated(dto_class, data):
    serializer = dto_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class PropertiesView(PermissionedView):
    required_permissions = {"GET": "properties.admin_view", "POST": "properties.admin_manage"}

    """List and create share one path, so they share one class."""

    @extend_schema(
        operation_id="properties_list",
        parameters=[dtos.PropertyListQueryDto],
        responses=resources.PropertyPageResource,
    )
    def get(self, request):
        query = _validated(dtos.PropertyListQueryDto, request.query_params)
        properties = services.list_properties(q=query.get("q"), status=query.get("status"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(properties, request, view=self)
        return paginator.get_paginated_response(
            resources.PropertySummaryResource(page, many=True).data
        )

    @extend_schema(
        operation_id="properties_create",
        request=dtos.CreatePropertyDto,
        responses={201: resources.PropertyDetailResource},
    )
    def post(self, request):
        data = _validated(dtos.CreatePropertyDto, request.data)
        owner_id = data.pop("owner_id")
        created = services.create_property(actor=request.user, owner_id=owner_id, fields=data)
        return Response(resources.PropertyDetailResource(created).data, status=201)


class OwnerOptionsView(PermissionedView):
    required_permissions = {"GET": "properties.admin_manage"}

    @extend_schema(
        operation_id="properties_owner_options",
        parameters=[dtos.OwnerOptionQueryDto],
        responses=resources.OwnerOptionResource(many=True),
    )
    def get(self, request):
        query = _validated(dtos.OwnerOptionQueryDto, request.query_params)
        landlords = services.list_owner_options(q=query.get("q"))
        return Response(resources.OwnerOptionResource(landlords, many=True).data)


class PropertyDetailView(PermissionedView):
    required_permissions = {
        "GET": "properties.admin_view",
        "PATCH": "properties.admin_manage",
        "DELETE": "properties.admin_manage",
    }

    """Read, edit and remove share one path, so they share one class."""

    @extend_schema(operation_id="properties_get", responses=resources.PropertyDetailResource)
    def get(self, request, property_id):
        found = services.get_property(property_id=property_id)
        return Response(resources.PropertyDetailResource(found).data)

    @extend_schema(
        operation_id="properties_update",
        request=dtos.UpdatePropertyDto,
        responses=resources.PropertyDetailResource,
    )
    def patch(self, request, property_id):
        changes = _validated(dtos.UpdatePropertyDto, request.data)
        updated = services.update_property(
            actor=request.user, property_id=property_id, changes=changes
        )
        return Response(resources.PropertyDetailResource(updated).data)

    @extend_schema(operation_id="properties_delete", responses={204: None})
    def delete(self, request, property_id):
        services.delete_property(actor=request.user, property_id=property_id)
        return Response(status=204)


class UnitsView(PermissionedView):
    required_permissions = {"POST": "properties.admin_manage"}

    @extend_schema(
        operation_id="properties_units_create",
        request=dtos.UnitFieldsDto,
        responses={201: resources.UnitResource},
    )
    def post(self, request, property_id):
        fields = _validated(dtos.UnitFieldsDto, request.data)
        unit = services.create_unit(actor=request.user, property_id=property_id, fields=fields)
        return Response(resources.UnitResource(unit).data, status=201)


class UnitDetailView(PermissionedView):
    required_permissions = {"PATCH": "properties.admin_manage", "DELETE": "properties.admin_manage"}

    @extend_schema(
        operation_id="properties_units_update",
        request=dtos.UpdateUnitDto,
        responses=resources.UnitResource,
    )
    def patch(self, request, property_id, unit_id):
        changes = _validated(dtos.UpdateUnitDto, request.data)
        unit = services.update_unit(
            actor=request.user, property_id=property_id, unit_id=unit_id, changes=changes
        )
        return Response(resources.UnitResource(unit).data)

    @extend_schema(operation_id="properties_units_delete", responses={204: None})
    def delete(self, request, property_id, unit_id):
        services.delete_unit(actor=request.user, property_id=property_id, unit_id=unit_id)
        return Response(status=204)


class UnitOccupancyView(PermissionedView):
    required_permissions = {"POST": "properties.admin_manage"}

    @extend_schema(
        operation_id="properties_units_occupancy",
        request=dtos.ChangeOccupancyDto,
        responses=resources.UnitResource,
    )
    def post(self, request, property_id, unit_id):
        data = _validated(dtos.ChangeOccupancyDto, request.data)
        unit = services.change_unit_occupancy(
            actor=request.user,
            property_id=property_id,
            unit_id=unit_id,
            occupancy_status=data["occupancy_status"],
        )
        return Response(resources.UnitResource(unit).data)
