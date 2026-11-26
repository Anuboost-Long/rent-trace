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


class RequestCorrectionDto(serializers.Serializer):
    record_id = serializers.IntegerField(help_text="The condition note to correct.")
    title = serializers.CharField(max_length=200, required=False)
    what_is_incorrect = serializers.CharField()
    proposed_replacement = serializers.CharField(help_text="The corrected description.")
    why_change_needed = serializers.CharField()


CORRECTION_STATUSES = [
    ReviewStatus.PENDING_REVIEW,
    ReviewStatus.APPROVED,
    ReviewStatus.REJECTED,
    ReviewStatus.STALE,
    ReviewStatus.CANCELLED,
]


class CorrectionListQueryDto(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=CORRECTION_STATUSES,
        required=False,
        help_text="Defaults to the corrections waiting for a decision.",
    )


class UnitCorrectionsQueryDto(serializers.Serializer):
    unit_id = serializers.IntegerField()


class RequestRemovalDto(serializers.Serializer):
    record_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=20,
        help_text="Condition records.",
    )
    reason = serializers.CharField()
    include_descendants = serializers.BooleanField(
        default=True, help_text="Also hide related records and attached photos."
    )


REMOVAL_STATUSES = CORRECTION_STATUSES


class RemovalListQueryDto(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=REMOVAL_STATUSES,
        required=False,
        help_text="Defaults to the removal requests waiting for a decision.",
    )
