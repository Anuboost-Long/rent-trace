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


class AddEvidencePhotoDto(serializers.Serializer):
    file = serializers.FileField(help_text="A JPEG or PNG photo, up to 10 MB.")


class RequestInformationDto(DecideCaseDto):
    pass


class RespondToInformationDto(serializers.Serializer):
    message = serializers.CharField(help_text="Your answer to the landlord's question.")
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    observed_at = serializers.DateTimeField(required=False)
