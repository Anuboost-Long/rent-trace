from rest_framework import serializers

from properties.models import PropertyFileKind


class AddPropertyFileDto(serializers.Serializer):
    file = serializers.FileField(help_text="A JPEG or PNG photo, or a PDF document. Up to 10 MB.")
    kind = serializers.ChoiceField(choices=PropertyFileKind.values)
    caption = serializers.CharField(
        max_length=200, required=False, allow_null=True, allow_blank=True
    )
