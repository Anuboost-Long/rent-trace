from rest_framework import serializers


class AcceptInvitationDto(serializers.Serializer):
    token = serializers.CharField(max_length=255)
