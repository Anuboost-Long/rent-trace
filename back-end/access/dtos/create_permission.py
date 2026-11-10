from rest_framework import serializers

CODE_PATTERN = r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$"


class CreatePermissionDto(serializers.Serializer):
    code = serializers.RegexField(
        CODE_PATTERN,
        max_length=100,
        help_text="module.action in lower case, for example reports.export.",
    )
    name = serializers.CharField(max_length=150)
    is_admin_only = serializers.BooleanField(default=False)
