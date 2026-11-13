from rest_framework import serializers

from providers.models import ServiceProvider


class ServiceProviderResource(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()

    class Meta:
        model = ServiceProvider
        fields = [
            "id",
            "business_name",
            "contact_name",
            "phone_number",
            "email",
            "website",
            "address",
            "description",
            "categories",
            "properties",
        ]

    def get_categories(self, provider) -> list[dict]:
        return [
            {"code": link.service_category.code, "name": link.service_category.name}
            for link in provider.live_categories
        ]

    def get_properties(self, provider) -> list[dict]:
        return [
            {
                "property_id": link.property_id,
                "property_name": link.property.property_name or link.property.address_line_1,
                "is_recommended": link.is_recommended,
                "contract_notes": link.contract_notes,
            }
            for link in provider.live_links
        ]
