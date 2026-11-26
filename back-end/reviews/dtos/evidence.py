from rest_framework import serializers


class SubmitEvidenceDto(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    observed_at = serializers.DateTimeField(help_text="When you saw the condition.")


class ApproveEvidenceDto(serializers.Serializer):
    idempotency_key = serializers.UUIDField(
        help_text="A fresh id per click. Sending the same one again changes nothing."
    )


class RejectEvidenceDto(ApproveEvidenceDto):
    reason = serializers.CharField()


class EvidenceListQueryDto(serializers.Serializer):
    unit_id = serializers.IntegerField()
