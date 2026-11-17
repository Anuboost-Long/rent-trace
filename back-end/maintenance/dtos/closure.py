from rest_framework import serializers

from maintenance.models import ClosureOutcome


class ClosureDto(serializers.Serializer):
    outcome = serializers.ChoiceField(choices=ClosureOutcome.values)
    reason = serializers.CharField(max_length=1000, help_text="Why it can be closed.")
