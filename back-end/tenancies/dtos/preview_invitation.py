from rest_framework import serializers


class PreviewInvitationDto(serializers.Serializer):
    token = serializers.CharField(max_length=255)
