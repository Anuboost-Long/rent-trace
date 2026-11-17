from rest_framework import serializers

from conditions.models import ConditionRecord


class TenantConditionResource(serializers.ModelSerializer):
    """What a tenant may see of a note the landlord chose to show."""

    title = serializers.CharField(source="accepted_version.title")
    description = serializers.CharField(source="accepted_version.condition_description")
    observed_at = serializers.DateTimeField(source="accepted_version.observed_at")

    class Meta:
        model = ConditionRecord
        fields = ["id", "title", "description", "observed_at"]


class ConditionResource(TenantConditionResource):
    unit_id = serializers.IntegerField(source="property_unit_id")
    version_no = serializers.IntegerField(source="accepted_version.version_no")

    class Meta(TenantConditionResource.Meta):
        fields = [
            *TenantConditionResource.Meta.fields,
            "unit_id",
            "is_shown_to_tenants",
            "version_no",
            "updated_at",
        ]
