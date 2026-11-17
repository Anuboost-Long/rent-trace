from rest_framework import serializers

from tenancies.models import Tenancy, TenancyParty, TermChangeStatus
from tenancies.resources.invitation import InvitationResource
from tenancies.resources.term_change import TermChangeResource


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
    pending_change = serializers.SerializerMethodField(
        help_text="A rent or bond increase waiting for the tenants, or null."
    )
    term_history = serializers.SerializerMethodField(
        help_text="Past rent and bond changes, newest first."
    )

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
            "rent_amount",
            "rent_frequency",
            "bond_amount",
            "currency",
            "unit",
            "property",
            "max_occupants",
            "people_count",
            "tenants",
            "invitations",
            "pending_change",
            "term_history",
        ]

    def get_max_occupants(self, tenancy) -> int | None:
        return tenancy.property_unit.max_occupants

    def get_people_count(self, tenancy) -> int:
        return len(tenancy.current_parties)

    def _people(self, tenancy):
        return [
            {
                "user_id": party.tenant_id,
                "name": f"{party.tenant.first_name} {party.tenant.last_name}",
            }
            for party in tenancy.current_parties
        ]

    def get_pending_change(self, tenancy) -> dict | None:
        pending = next(
            (c for c in tenancy.all_term_changes if c.status == TermChangeStatus.PENDING), None
        )
        if pending is None:
            return None
        return TermChangeResource(pending, context={"people": self._people(tenancy)}).data

    def get_term_history(self, tenancy) -> list[dict]:
        past = [c for c in tenancy.all_term_changes if c.status != TermChangeStatus.PENDING]
        return TermChangeResource(past[:20], many=True).data

    def get_unit(self, tenancy) -> dict:
        unit = tenancy.property_unit
        return {"id": unit.pk, "name": unit.name}

    def get_property(self, tenancy) -> dict:
        place = tenancy.property_unit.property
        return {"id": place.pk, "name": place.property_name, "suburb": place.suburb}
