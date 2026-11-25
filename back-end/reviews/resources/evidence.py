from typing import Literal

from rest_framework import serializers

from reviews.models import ReviewDecisionType, ReviewRequest, ReviewStatus
from reviews.services.shared.decisions import is_expired


class EvidenceResource(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(
        help_text="EXPIRED when it waited 14 days for an answer; the stored status is unchanged."
    )
    title = serializers.CharField(source="current_submission.proposed_condition_version.title")
    description = serializers.CharField(
        source="current_submission.proposed_condition_version.condition_description",
        allow_null=True,
    )
    observed_at = serializers.DateTimeField(
        source="current_submission.proposed_condition_version.observed_at"
    )
    unit_id = serializers.IntegerField(source="target.condition_record.property_unit_id")
    tenancy_id = serializers.IntegerField(source="target.condition_record.tenancy_id")
    author = serializers.SerializerMethodField()
    rejection_reason = serializers.SerializerMethodField(
        help_text="Why the landlord rejected it, or null."
    )

    class Meta:
        model = ReviewRequest
        fields = [
            "id",
            "status",
            "title",
            "description",
            "observed_at",
            "unit_id",
            "tenancy_id",
            "author",
            "rejection_reason",
            "submitted_at",
            "completed_at",
        ]

    def get_status(self, request) -> Literal[*ReviewStatus.values, "EXPIRED"]:
        return "EXPIRED" if is_expired(request) else request.status

    def get_author(self, request) -> str:
        return f"{request.requested_by.first_name} {request.requested_by.last_name}"

    def get_rejection_reason(self, request) -> str | None:
        rejection = next(
            (d for d in request.decisions.all() if d.decision == ReviewDecisionType.REJECT), None
        )
        return rejection.reason if rejection else None
