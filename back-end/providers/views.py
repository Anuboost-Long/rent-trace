from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from common.pagination import PagePagination
from properties.landlord_views import LandlordView
from providers import dtos, resources, services


def _validated(dto_class, data):
    serializer = dto_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class ProvidersView(LandlordView):
    required_permissions = {"GET": "providers.view", "POST": "providers.manage"}

    @extend_schema(
        operation_id="landlord_providers_list",
        parameters=[dtos.ProviderListQueryDto],
        responses=resources.ProviderPageResource,
    )
    def get(self, request):
        query = _validated(dtos.ProviderListQueryDto, request.query_params)
        providers = services.list_providers(
            owner=request.user, q=query.get("q"), category=query.get("category")
        )
        paginator = PagePagination()
        page = paginator.paginate_queryset(providers, request, view=self)
        return paginator.get_paginated_response(
            resources.ServiceProviderResource(page, many=True).data
        )

    @extend_schema(
        operation_id="landlord_providers_create",
        request=dtos.ProviderFieldsDto,
        responses={201: resources.ServiceProviderResource},
    )
    def post(self, request):
        fields = _validated(dtos.ProviderFieldsDto, request.data)
        created = services.create_provider(actor=request.user, fields=fields)
        return Response(resources.ServiceProviderResource(created).data, status=201)


class ProviderDetailView(LandlordView):
    required_permissions = {
        "GET": "providers.view",
        "PATCH": "providers.manage",
        "DELETE": "providers.manage",
    }

    @extend_schema(
        operation_id="landlord_providers_get", responses=resources.ServiceProviderResource
    )
    def get(self, request, provider_id):
        found = services.get_provider(owner=request.user, provider_id=provider_id)
        return Response(resources.ServiceProviderResource(found).data)

    @extend_schema(
        operation_id="landlord_providers_update",
        request=dtos.UpdateProviderDto,
        responses=resources.ServiceProviderResource,
    )
    def patch(self, request, provider_id):
        changes = _validated(dtos.UpdateProviderDto, request.data)
        updated = services.update_provider(
            actor=request.user, provider_id=provider_id, changes=changes
        )
        return Response(resources.ServiceProviderResource(updated).data)

    @extend_schema(operation_id="landlord_providers_delete", responses={204: None})
    def delete(self, request, provider_id):
        services.delete_provider(actor=request.user, provider_id=provider_id)
        return Response(status=204)


class ServiceCategoriesView(LandlordView):
    required_permissions = {"GET": "providers.view"}

    @extend_schema(
        operation_id="landlord_provider_categories_list",
        responses=resources.ServiceCategoryResource(many=True),
    )
    def get(self, request):
        return Response(
            resources.ServiceCategoryResource(services.list_categories(), many=True).data
        )
