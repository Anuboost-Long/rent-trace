from rest_framework import serializers


class MfaBackupCodesResource(serializers.Serializer):
    backup_codes = serializers.ListField(
        child=serializers.CharField(), help_text="Shown once. Each code works one time."
    )
