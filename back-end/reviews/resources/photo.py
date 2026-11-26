from rest_framework import serializers

from files.models import File


class EvidencePhotoResource(serializers.ModelSerializer):
    name = serializers.CharField(source="original_name")

    class Meta:
        model = File
        fields = ["id", "name"]
