from django.http import FileResponse
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from properties import dtos, resources, services

CONTENT_CACHE = "private, max-age=3600"


def _validated(dto_class, data):
    serializer = dto_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class PropertyFilesBase(PermissionedView):
    """Shared by the admin and landlord routes; a landlord view narrows `scope` to their own properties."""

    def scope(self, request):
        return None


class PropertyFilesView(PropertyFilesBase):
    required_permissions = {"POST": "properties.admin_manage"}
    parser_classes = [MultiPartParser]

    @extend_schema(
        request={"multipart/form-data": dtos.AddPropertyFileDto},
        responses={201: resources.PropertyFileResource},
    )
    def post(self, request, property_id, unit_id=None):
        data = _validated(dtos.AddPropertyFileDto, request.data)
        added = services.add_property_file(
            actor=request.user,
            property_id=property_id,
            upload=data["file"],
            kind=data["kind"],
            caption=data.get("caption"),
            owned_by=self.scope(request),
            unit_id=unit_id,
        )
        return Response(resources.PropertyFileResource(added).data, status=201)


class PropertyFileDetailView(PropertyFilesBase):
    required_permissions = {
        "PATCH": "properties.admin_manage",
        "DELETE": "properties.admin_manage",
    }

    @extend_schema(request=dtos.UpdatePropertyFileDto, responses=resources.PropertyFileResource)
    def patch(self, request, property_id, file_id, unit_id=None):
        changes = _validated(dtos.UpdatePropertyFileDto, request.data)
        updated = services.update_property_file(
            actor=request.user,
            property_id=property_id,
            property_file_id=file_id,
            changes=changes,
            owned_by=self.scope(request),
            unit_id=unit_id,
        )
        return Response(resources.PropertyFileResource(updated).data)

    @extend_schema(responses={204: None})
    def delete(self, request, property_id, file_id, unit_id=None):
        services.delete_property_file(
            actor=request.user,
            property_id=property_id,
            property_file_id=file_id,
            owned_by=self.scope(request),
            unit_id=unit_id,
        )
        return Response(status=204)


class PropertyFileContentView(PropertyFilesBase):
    required_permissions = {"GET": "properties.admin_view"}

    @extend_schema(responses={(200, "application/octet-stream"): bytes})
    def get(self, request, property_id, file_id, unit_id=None):
        stored, content = services.open_property_file(
            property_id=property_id,
            property_file_id=file_id,
            owned_by=self.scope(request),
            unit_id=unit_id,
        )
        response = FileResponse(
            content, content_type=stored.mime_type, filename=stored.original_name
        )
        response["Cache-Control"] = CONTENT_CACHE
        return response


class ListingStatusView(PropertyFilesBase):
    required_permissions = {"POST": "properties.admin_manage"}
    as_admin = True

    @extend_schema(request=dtos.ChangeListingDto, responses=resources.PropertyDetailResource)
    def post(self, request, property_id):
        data = _validated(dtos.ChangeListingDto, request.data)
        changed = services.change_listing_status(
            actor=request.user,
            property_id=property_id,
            listing_status=data["listing_status"],
            owned_by=self.scope(request),
            as_admin=self.as_admin,
        )
        return Response(resources.PropertyDetailResource(changed).data)
