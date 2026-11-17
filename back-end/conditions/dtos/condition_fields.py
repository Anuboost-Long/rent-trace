from rest_framework import serializers


class CreateConditionDto(serializers.Serializer):
    unit_id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    observed_at = serializers.DateTimeField(help_text="When the unit was checked.")
    is_shown_to_tenants = serializers.BooleanField(required=False)


class UpdateConditionDto(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    observed_at = serializers.DateTimeField(required=False)
    is_shown_to_tenants = serializers.BooleanField(required=False)


class ConditionListQueryDto(serializers.Serializer):
    unit_id = serializers.IntegerField()
