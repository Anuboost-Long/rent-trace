from drf_spectacular.utils import extend_schema
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from accounts.services.shared.account_rules import has_role
from common.pagination import PagePagination
from properties import dtos, file_views, resources, services


def _validated(dto_class, data):
    serializer = dto_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class IsLandlord(BasePermission):
    message = "Only landlords can use this."

    def has_permission(self, request, view):
        return has_role(request.user, "LANDLORD")


class LandlordView(PermissionedView):
    """Every landlord endpoint only sees the properties the signed-in landlord owns."""

    permission_classes = [*PermissionedView.permission_classes, IsLandlord]


class LandlordPropertiesView(LandlordView):
    required_permissions = {"GET": "properties.view", "POST": "properties.create"}

    @extend_schema(
        operation_id="landlord_properties_list",
        parameters=[dtos.PropertyListQueryDto],
        responses=resources.PropertyPageResource,
    )
    def get(self, request):
        query = _validated(dtos.PropertyListQueryDto, request.query_params)
        properties = services.list_properties(
            q=query.get("q"), status=query.get("status"), owned_by=request.user
        )
        paginator = PagePagination()
        page = paginator.paginate_queryset(properties, request, view=self)
        return paginator.get_paginated_response(
            resources.PropertySummaryResource(page, many=True).data
        )

    @extend_schema(
        operation_id="landlord_properties_create",
        request=dtos.PropertyFieldsDto,
        responses={201: resources.PropertyDetailResource},
    )
    def post(self, request):
        fields = _validated(dtos.PropertyFieldsDto, request.data)
        created = services.create_property(
            actor=request.user, owner_id=request.user.pk, fields=fields
        )
        return Response(resources.PropertyDetailResource(created).data, status=201)


class LandlordPropertyDetailView(LandlordView):
    required_permissions = {"GET": "properties.view", "PATCH": "properties.update"}

    @extend_schema(
        operation_id="landlord_properties_get", responses=resources.PropertyDetailResource
    )
    def get(self, request, property_id):
        found = services.get_property(property_id=property_id, owned_by=request.user)
        return Response(resources.PropertyDetailResource(found).data)

    @extend_schema(
        operation_id="landlord_properties_update",
        request=dtos.UpdatePropertyDto,
        responses=resources.PropertyDetailResource,
    )
    def patch(self, request, property_id):
        changes = _validated(dtos.UpdatePropertyDto, request.data)
        updated = services.update_property(
            actor=request.user,
            property_id=property_id,
            changes=changes,
            owned_by=request.user,
        )
        return Response(resources.PropertyDetailResource(updated).data)


class LandlordUnitsView(LandlordView):
    required_permissions = {"POST": "properties.update"}

    @extend_schema(
        operation_id="landlord_properties_units_create",
        request=dtos.UnitFieldsDto,
        responses={201: resources.UnitResource},
    )
    def post(self, request, property_id):
        fields = _validated(dtos.UnitFieldsDto, request.data)
        unit = services.create_unit(
            actor=request.user, property_id=property_id, fields=fields, owned_by=request.user
        )
        return Response(resources.UnitResource(unit).data, status=201)


class LandlordUnitDetailView(LandlordView):
    required_permissions = {"PATCH": "properties.update", "DELETE": "properties.update"}

    @extend_schema(
        operation_id="landlord_properties_units_update",
        request=dtos.UpdateUnitDto,
        responses=resources.UnitResource,
    )
    def patch(self, request, property_id, unit_id):
        changes = _validated(dtos.UpdateUnitDto, request.data)
        unit = services.update_unit(
            actor=request.user,
            property_id=property_id,
            unit_id=unit_id,
            changes=changes,
            owned_by=request.user,
        )
        return Response(resources.UnitResource(unit).data)

    @extend_schema(operation_id="landlord_properties_units_delete", responses={204: None})
    def delete(self, request, property_id, unit_id):
        services.delete_unit(
            actor=request.user,
            property_id=property_id,
            unit_id=unit_id,
            owned_by=request.user,
        )
        return Response(status=204)


class LandlordUnitOccupancyView(LandlordView):
    required_permissions = {"POST": "properties.update"}

    @extend_schema(
        operation_id="landlord_properties_units_occupancy",
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
            owned_by=request.user,
        )
        return Response(resources.UnitResource(unit).data)


class LandlordScope:
    """Narrows the shared file views to properties the signed-in landlord owns."""

    permission_classes = [*PermissionedView.permission_classes, IsLandlord]

    def scope(self, request):
        return request.user


class LandlordPropertyFilesView(LandlordScope, file_views.PropertyFilesView):
    required_permissions = {"POST": "properties.update"}


class LandlordPropertyFileDetailView(LandlordScope, file_views.PropertyFileDetailView):
    required_permissions = {"PATCH": "properties.update", "DELETE": "properties.update"}


class LandlordPropertyFileContentView(LandlordScope, file_views.PropertyFileContentView):
    required_permissions = {"GET": "properties.view"}


class LandlordListingStatusView(LandlordScope, file_views.ListingStatusView):
    required_permissions = {"POST": "properties.publish"}
    as_admin = False
