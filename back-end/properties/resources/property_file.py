from rest_framework import serializers

from properties.models import PropertyFile


class PropertyFileResource(serializers.ModelSerializer):
    original_name = serializers.CharField(source="file.original_name")
    mime_type = serializers.CharField(source="file.mime_type")
    size_bytes = serializers.IntegerField(source="file.size_bytes")
    unit_id = serializers.IntegerField(source="property_unit_id", allow_null=True)

    class Meta:
        model = PropertyFile
        fields = [
            "id",
            "unit_id",
            "kind",
            "caption",
            "is_cover",
            "sort_order",
            "original_name",
            "mime_type",
            "size_bytes",
            "created_at",
        ]
