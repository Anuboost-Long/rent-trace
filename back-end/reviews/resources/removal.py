from rest_framework import serializers

from reviews.models import ReviewRequest
from reviews.resources.shared import admin_decision, name_of


class RemovalItemResource(serializers.Serializer):
    record_id = serializers.IntegerField(source="target.condition_record_id")
    title = serializers.SerializerMethodField()
    include_descendants = serializers.BooleanField()

    def get_title(self, item) -> str | None:
        versions = item.target.condition_record.versions.all()
        return max(versions, key=lambda v: v.version_no).title if versions else None


class RemovalResource(serializers.ModelSerializer):
    requested_by_name = serializers.SerializerMethodField()
    reason = serializers.CharField(source="current_submission.reason")
    items = RemovalItemResource(source="removal_items", many=True)
    admin_reason = serializers.SerializerMethodField(help_text="Null until an admin decides.")

    class Meta:
        model = ReviewRequest
        fields = [
            "id",
            "status",
            "requester_side",
            "requested_by_name",
            "reason",
            "items",
            "admin_reason",
            "submitted_at",
            "completed_at",
        ]

    def get_requested_by_name(self, request) -> str:
        return name_of(request.requested_by)

    def get_admin_reason(self, request) -> str | None:
        decision = admin_decision(request)
        return decision.reason if decision else None
