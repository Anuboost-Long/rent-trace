from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from providers import dtos, resources, services
from providers.views import _validated


class AdminProvidersView(PermissionedView):
    required_permissions = {"GET": "providers.admin_view"}

    @extend_schema(
        operation_id="admin_providers_list",
        parameters=[dtos.ProviderListQueryDto],
        responses=resources.AdminProviderPageResource,
    )
    def get(self, request):
        query = _validated(dtos.ProviderListQueryDto, request.query_params)
        providers = services.list_all_providers(q=query.get("q"), category=query.get("category"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(providers, request, view=self)
        return paginator.get_paginated_response(
            resources.AdminServiceProviderResource(page, many=True).data
        )


class AdminServiceCategoriesView(PermissionedView):
    required_permissions = {"GET": "providers.admin_view"}

    @extend_schema(
        operation_id="admin_provider_categories_list",
        responses=resources.ServiceCategoryResource(many=True),
    )
    def get(self, request):
        return Response(
            resources.ServiceCategoryResource(services.list_categories(), many=True).data
        )
