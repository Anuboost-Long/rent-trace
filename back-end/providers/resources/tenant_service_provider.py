from rest_framework import serializers

from providers.models import ServiceProvider


class TenantServiceProviderResource(serializers.ModelSerializer):
    is_recommended = serializers.BooleanField()
    categories = serializers.SerializerMethodField()

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
            "is_recommended",
            "categories",
        ]

    def get_categories(self, provider) -> list[dict]:
        return [
            {"code": link.service_category.code, "name": link.service_category.name}
            for link in provider.live_categories
        ]
