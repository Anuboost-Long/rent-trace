from datetime import datetime

from rest_framework import serializers

from reviews.models import ReviewRequest
from reviews.resources.shared import (
    admin_decision,
    escalation,
    landlord_rejection,
    name_of,
    place_of,
)


class CaseResource(serializers.ModelSerializer):
    report_id = serializers.IntegerField(source="parent_request_id")
    title = serializers.CharField(
        source="parent_request.current_submission.proposed_condition_version.title"
    )
    description = serializers.CharField(
        source="parent_request.current_submission.proposed_condition_version.condition_description",
        allow_null=True,
    )
    observed_at = serializers.DateTimeField(
        source="parent_request.current_submission.proposed_condition_version.observed_at"
    )
    unit_id = serializers.IntegerField(
        source="parent_request.target.condition_record.property_unit_id"
    )
    tenancy_id = serializers.IntegerField(
        source="parent_request.target.condition_record.tenancy_id"
    )
    place = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField(help_text="The tenant who wrote the report.")
    landlord_rejection_reason = serializers.SerializerMethodField()
    escalated_by = serializers.SerializerMethodField()
    escalated_at = serializers.SerializerMethodField()
    escalation_reason = serializers.SerializerMethodField()
    admin_reason = serializers.SerializerMethodField(help_text="Null until an admin decides.")

    class Meta:
        model = ReviewRequest
        fields = [
            "id",
            "status",
            "report_id",
            "title",
            "description",
            "observed_at",
            "unit_id",
            "tenancy_id",
            "place",
            "author",
            "landlord_rejection_reason",
            "escalated_by",
            "escalated_at",
            "escalation_reason",
            "admin_reason",
            "completed_at",
        ]

    def get_place(self, case) -> str:
        return place_of(case.parent_request)

    def get_author(self, case) -> str:
        return name_of(case.parent_request.requested_by)

    def get_landlord_rejection_reason(self, case) -> str | None:
        rejection = landlord_rejection(case.parent_request)
        return rejection.reason if rejection else None

    def get_escalated_by(self, case) -> str | None:
        row = escalation(case)
        return name_of(row.actor) if row else None

    def get_escalated_at(self, case) -> datetime | None:
        row = escalation(case)
        return row.created_at if row else None

    def get_escalation_reason(self, case) -> str | None:
        row = escalation(case)
        return row.reason if row else None

    def get_admin_reason(self, case) -> str | None:
        decision = admin_decision(case)
        return decision.reason if decision else None
