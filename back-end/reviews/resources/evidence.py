from datetime import datetime
from typing import Literal

from rest_framework import serializers

from reviews.models import ReviewRequest, ReviewStatus
from reviews.resources.shared import admin_decision, escalation, landlord_rejection, name_of
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
    escalated_at = serializers.SerializerMethodField(
        help_text="When someone asked an admin to decide, or null."
    )
    admin_reason = serializers.SerializerMethodField(
        help_text="Why the admin approved or rejected it, or null until they decide."
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
            "escalated_at",
            "admin_reason",
            "submitted_at",
            "completed_at",
        ]

    def get_status(self, request) -> Literal[*ReviewStatus.values, "EXPIRED"]:
        return "EXPIRED" if is_expired(request) else request.status

    def _case(self, request):
        return next(iter(request.dispute_cases), None)

    def get_author(self, request) -> str:
        return name_of(request.requested_by)

    def get_rejection_reason(self, request) -> str | None:
        rejection = landlord_rejection(request)
        return rejection.reason if rejection else None

    def get_escalated_at(self, request) -> datetime | None:
        row = escalation(self._case(request))
        return row.created_at if row else None

    def get_admin_reason(self, request) -> str | None:
        case = self._case(request)
        decision = admin_decision(case) if case else None
        return decision.reason if decision else None
