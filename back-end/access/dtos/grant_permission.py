from rest_framework import serializers


class GrantPermissionDto(serializers.Serializer):
    permission = serializers.CharField(max_length=100, help_text="A permission code.")
    reason = serializers.CharField(max_length=500, help_text="Why this person needs it.")
