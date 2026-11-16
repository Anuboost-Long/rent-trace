from rest_framework import serializers

from providers.resources.tenant_service_provider import TenantServiceProviderResource


class PropertyProviderResource(TenantServiceProviderResource):
    """A saved tradesperson as it stands on one property, with the landlord's private notes."""

    contract_notes = serializers.CharField(allow_null=True)

    class Meta(TenantServiceProviderResource.Meta):
        fields = [*TenantServiceProviderResource.Meta.fields, "contract_notes"]
