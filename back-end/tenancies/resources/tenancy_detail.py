from rest_framework import serializers

from tenancies.models import Tenancy, TenancyParty
from tenancies.resources.invitation import InvitationResource


class TenantResource(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="tenant_id")
    first_name = serializers.CharField(source="tenant.first_name")
    last_name = serializers.CharField(source="tenant.last_name")

    class Meta:
        model = TenancyParty
        fields = ["user_id", "first_name", "last_name", "is_primary", "joined_at"]


class TenancyDetailResource(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    property = serializers.SerializerMethodField()
    tenants = TenantResource(source="current_parties", many=True)
    invitations = InvitationResource(source="all_invitations", many=True)
    max_occupants = serializers.SerializerMethodField()
    people_count = serializers.SerializerMethodField()

    class Meta:
        model = Tenancy
        fields = [
            "id",
            "reference_no",
            "status",
            "tenancy_type",
            "start_date",
            "end_date",
            "notes",
            "unit",
            "property",
            "max_occupants",
            "people_count",
            "tenants",
            "invitations",
        ]

    def get_max_occupants(self, tenancy) -> int | None:
        return tenancy.property_unit.max_occupants

    def get_people_count(self, tenancy) -> int:
        return len(tenancy.current_parties)

    def get_unit(self, tenancy) -> dict:
        unit = tenancy.property_unit
        return {"id": unit.pk, "name": unit.name}

    def get_property(self, tenancy) -> dict:
        place = tenancy.property_unit.property
        return {"id": place.pk, "name": place.property_name, "suburb": place.suburb}
