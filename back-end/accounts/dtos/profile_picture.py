from rest_framework import serializers


class ProfilePictureDto(serializers.Serializer):
    file = serializers.FileField(help_text="A JPEG or PNG image, up to 10 MB.")
