from rest_framework import serializers

from properties.models import PropertyUnit


class UnitResource(serializers.ModelSerializer):
    class Meta:
        model = PropertyUnit
        fields = [
            "id",
            "name",
            "unit_number",
            "unit_type",
            "description",
            "is_public",
            "occupancy_status",
            "rent_amount",
            "rent_frequency",
        ]
