from rest_framework import serializers

from tenancies.resources.my_tenancy import MyTenancyResource


class MyTenancyDetailResource(MyTenancyResource):
    housemates = serializers.SerializerMethodField(help_text="Other current tenants, names only.")

    class Meta(MyTenancyResource.Meta):
        fields = [*MyTenancyResource.Meta.fields, "housemates"]

    def get_housemates(self, tenancy) -> list[dict]:
        return [
            {
                "first_name": party.tenant.first_name,
                "last_name": party.tenant.last_name,
                "is_primary": party.is_primary,
            }
            for party in tenancy.housemates
        ]
