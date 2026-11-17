from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from properties.landlord_views import LandlordView
from providers import dtos, resources, services
from providers.views import _validated


class PropertyProvidersView(LandlordView):
    required_permissions = {"GET": "providers.view", "POST": "providers.manage"}

    @extend_schema(
        operation_id="landlord_property_providers_list",
        responses=resources.PropertyProviderResource(many=True),
    )
    def get(self, request, property_id):
        found = services.list_property_providers(owner=request.user, property_id=property_id)
        return Response(resources.PropertyProviderResource(found, many=True).data)

    @extend_schema(
        operation_id="landlord_property_providers_link",
        request=dtos.LinkProvidersDto,
        responses=resources.PropertyProviderResource(many=True),
    )
    def post(self, request, property_id):
        fields = _validated(dtos.LinkProvidersDto, request.data)
        found = services.link_providers(
            actor=request.user, property_id=property_id, provider_ids=fields["provider_ids"]
        )
        return Response(resources.PropertyProviderResource(found, many=True).data)


class PropertyProviderLinkView(LandlordView):
    required_permissions = {"PATCH": "providers.manage", "DELETE": "providers.manage"}

    @extend_schema(
        operation_id="landlord_property_providers_update",
        request=dtos.UpdateProviderLinkDto,
        responses=resources.PropertyProviderResource,
    )
    def patch(self, request, property_id, provider_id):
        changes = _validated(dtos.UpdateProviderLinkDto, request.data)
        found = services.update_property_provider(
            actor=request.user, property_id=property_id, provider_id=provider_id, changes=changes
        )
        return Response(resources.PropertyProviderResource(found).data)

    @extend_schema(operation_id="landlord_property_providers_unlink", responses={204: None})
    def delete(self, request, property_id, provider_id):
        services.unlink_provider(
            actor=request.user, property_id=property_id, provider_id=provider_id
        )
        return Response(status=204)
