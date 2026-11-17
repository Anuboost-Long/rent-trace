from rest_framework import serializers

from properties.models import Property
from properties.resources.owner import OwnerOptionResource


class PropertySummaryResource(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    unit_count = serializers.IntegerField()

    class Meta:
        model = Property
        fields = [
            "id",
            "property_name",
            "address_line_1",
            "address_line_2",
            "suburb",
            "state",
            "postcode",
            "country",
            "property_type",
            "property_status",
            "listing_status",
            "owner",
            "unit_count",
            "created_at",
        ]

    def get_owner(self, property_) -> dict | None:
        primary = next((o for o in property_.current_owners if o.is_primary_owner), None)
        return OwnerOptionResource(primary.owner).data if primary else None
