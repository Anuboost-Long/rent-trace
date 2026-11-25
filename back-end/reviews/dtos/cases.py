from rest_framework import serializers

from reviews.dtos.evidence import ApproveEvidenceDto
from reviews.models import ReviewStatus


class EscalateEvidenceDto(serializers.Serializer):
    reason = serializers.CharField(help_text="Why an admin should decide.")


class DecideCaseDto(ApproveEvidenceDto):
    reason = serializers.CharField()


class CaseListQueryDto(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[ReviewStatus.PENDING_REVIEW, ReviewStatus.APPROVED, ReviewStatus.REJECTED],
        required=False,
        help_text="Defaults to the cases waiting for a decision.",
    )
