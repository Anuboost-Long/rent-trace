from rest_framework import serializers

from tenancies.models import Tenancy
from tenancies.services.shared.invitations import CLOSED_STATUSES


class MyTenancyResource(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    property = serializers.SerializerMethodField()
    landlord = serializers.SerializerMethodField(help_text="Name only; no contact details.")
    is_primary = serializers.SerializerMethodField()
    joined_at = serializers.SerializerMethodField()
    left_at = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()
    max_occupants = serializers.SerializerMethodField()
    people_count = serializers.SerializerMethodField()

    class Meta:
        model = Tenancy
        fields = [
            "id",
            "reference_no",
            "status",
            "start_date",
            "end_date",
            "rent_amount",
            "rent_frequency",
            "bond_amount",
            "currency",
            "unit",
            "property",
            "landlord",
            "is_primary",
            "joined_at",
            "left_at",
            "is_current",
            "max_occupants",
            "people_count",
        ]

    def _party(self, tenancy):
        return tenancy.my_parties[0]

    def get_unit(self, tenancy) -> dict:
        unit = tenancy.property_unit
        return {"id": unit.pk, "name": unit.name}

    def get_property(self, tenancy) -> dict:
        place = tenancy.property_unit.property
        return {
            "id": place.pk,
            "name": place.property_name,
            "suburb": place.suburb,
            "state": place.state,
        }

    def get_landlord(self, tenancy) -> str | None:
        owners = tenancy.property_unit.property.current_owners
        return f"{owners[0].owner.first_name} {owners[0].owner.last_name}" if owners else None

    def get_is_primary(self, tenancy) -> bool:
        return self._party(tenancy).is_primary

    def get_joined_at(self, tenancy) -> str:
        return self._party(tenancy).joined_at.isoformat()

    def get_left_at(self, tenancy) -> str | None:
        left = self._party(tenancy).left_at
        return left.isoformat() if left else None

    def get_max_occupants(self, tenancy) -> int | None:
        return tenancy.property_unit.max_occupants

    def get_people_count(self, tenancy) -> int:
        return len(tenancy.housemates) + (1 if self._party(tenancy).left_at is None else 0)

    def get_is_current(self, tenancy) -> bool:
        return self._party(tenancy).left_at is None and tenancy.status not in CLOSED_STATUSES
