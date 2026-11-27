from rest_framework import serializers

from reviews.models import ReviewRequest
from reviews.resources.shared import admin_decision, name_of, place_of


class CorrectionResource(serializers.ModelSerializer):
    record_id = serializers.IntegerField(source="target.condition_record_id")
    unit_id = serializers.IntegerField(source="target.condition_record.property_unit_id")
    place = serializers.SerializerMethodField()
    requested_by_name = serializers.SerializerMethodField()
    current_title = serializers.CharField(source="current_submission.before_values.title")
    current_description = serializers.CharField(
        source="current_submission.before_values.description", allow_null=True
    )
    proposed_title = serializers.CharField(source="current_submission.proposed_values.title")
    proposed_description = serializers.CharField(
        source="current_submission.proposed_values.description"
    )
    what_is_incorrect = serializers.CharField(source="current_submission.what_is_incorrect")
    why_change_needed = serializers.CharField(source="current_submission.why_change_needed")
    admin_reason = serializers.SerializerMethodField(help_text="Null until an admin decides.")

    class Meta:
        model = ReviewRequest
        fields = [
            "id",
            "status",
            "requester_side",
            "record_id",
            "unit_id",
            "place",
            "requested_by_name",
            "current_title",
            "current_description",
            "proposed_title",
            "proposed_description",
            "what_is_incorrect",
            "why_change_needed",
            "admin_reason",
            "submitted_at",
            "completed_at",
        ]

    def get_place(self, request) -> str:
        return place_of(request)

    def get_requested_by_name(self, request) -> str:
        return name_of(request.requested_by)

    def get_admin_reason(self, request) -> str | None:
        decision = admin_decision(request)
        return decision.reason if decision else None
