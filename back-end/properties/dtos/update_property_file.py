from rest_framework import serializers


class UpdatePropertyFileDto(serializers.Serializer):
    caption = serializers.CharField(
        max_length=200, required=False, allow_null=True, allow_blank=True
    )
    is_cover = serializers.BooleanField(required=False)
