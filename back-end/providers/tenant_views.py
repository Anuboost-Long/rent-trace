from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from providers import resources, services
from tenancies.tenant_views import TenantTenancyView


class MyPropertyProvidersView(TenantTenancyView):
    @extend_schema(
        operation_id="tenant_tenancies_providers_list",
        responses=resources.TenantServiceProviderResource(many=True),
    )
    def get(self, request, tenancy_id):
        found = services.list_my_property_providers(user=request.user, tenancy_id=tenancy_id)
        return Response(resources.TenantServiceProviderResource(found, many=True).data)
