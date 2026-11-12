from rest_framework import serializers

from tenancies.resources.housemate_request import HousemateRequestResource
from tenancies.resources.my_tenancy import MyTenancyResource


class MyTenancyDetailResource(MyTenancyResource):
    housemates = serializers.SerializerMethodField(help_text="Other current tenants, names only.")
    housemate_requests = HousemateRequestResource(
        source="my_requests", many=True, help_text="Only the requests this tenant made."
    )

    class Meta(MyTenancyResource.Meta):
        fields = [*MyTenancyResource.Meta.fields, "housemates", "housemate_requests"]

    def get_housemates(self, tenancy) -> list[dict]:
        return [
            {
                "first_name": party.tenant.first_name,
                "last_name": party.tenant.last_name,
                "is_primary": party.is_primary,
            }
            for party in tenancy.housemates
        ]
