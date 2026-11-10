from rest_framework import serializers


class CreateRoleDto(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    parent = serializers.CharField(
        max_length=30,
        required=False,
        allow_null=True,
        help_text="Code of a role to inherit permissions from.",
    )
    permissions = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False, default=list
    )
    reason = serializers.CharField(max_length=500, required=False)
