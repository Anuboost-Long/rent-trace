from rest_framework import serializers


class LiftBanDto(serializers.Serializer):
    reason = serializers.CharField(max_length=500, help_text="Why the ban is being lifted.")
