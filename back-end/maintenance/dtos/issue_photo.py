from rest_framework import serializers


class AddIssuePhotoDto(serializers.Serializer):
    file = serializers.FileField(help_text="A JPEG or PNG photo, up to 10 MB.")
    caption = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
