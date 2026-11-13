from rest_framework import serializers


class AssignProviderDto(serializers.Serializer):
    service_provider_id = serializers.IntegerField(min_value=1)
    scheduled_at = serializers.DateTimeField(
        required=False, allow_null=True, help_text="When they are due, if you know."
    )
