from rest_framework import serializers

from properties.models import OccupancyStatus

MANUAL_OCCUPANCY = [
    OccupancyStatus.VACANT,
    OccupancyStatus.PARTIALLY_OCCUPIED,
    OccupancyStatus.UNAVAILABLE,
]


class ChangeOccupancyDto(serializers.Serializer):
    occupancy_status = serializers.ChoiceField(choices=MANUAL_OCCUPANCY)
