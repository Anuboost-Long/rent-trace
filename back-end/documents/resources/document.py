from typing import Literal

from rest_framework import serializers

from documents.models import Document, DocumentFile, DocumentVersion
from reviews.models import ReviewDecisionType, ReviewStatus


class DocumentFileResource(serializers.ModelSerializer):
    id = serializers.IntegerField(source="file_id")
    name = serializers.CharField(source="file.original_name")
    mime_type = serializers.CharField(source="file.mime_type")
    size_bytes = serializers.IntegerField(source="file.size_bytes")

    class Meta:
        model = DocumentFile
        fields = ["id", "name", "mime_type", "size_bytes"]


class DocumentVersionResource(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    uploaded_at = serializers.DateTimeField(source="created_at")
    confirmation = serializers.SerializerMethodField(
        help_text="Null when no consent is needed; WAITING, CONFIRMED, FLAGGED or SUPERSEDED."
    )
    flag_reason = serializers.SerializerMethodField()
    files = DocumentFileResource(many=True)

    class Meta:
        model = DocumentVersion
        fields = [
            "id",
            "version_no",
            "title",
            "description",
            "document_date",
            "uploaded_by_name",
            "uploaded_at",
            "confirmation",
            "flag_reason",
            "files",
        ]

    def get_uploaded_by_name(self, version) -> str:
        person = version.uploaded_by
        return f"{person.first_name} {person.last_name}"

    def get_confirmation(
        self, version
    ) -> Literal["WAITING", "CONFIRMED", "FLAGGED", "SUPERSEDED"] | None:
        request = version.confirmation_request
        if request is None:
            return None
        return {
            ReviewStatus.PENDING_REVIEW: "WAITING",
            ReviewStatus.APPROVED: "CONFIRMED",
            ReviewStatus.REJECTED: "FLAGGED",
        }.get(request.status, "SUPERSEDED")

    def get_flag_reason(self, version) -> str | None:
        request = version.confirmation_request
        if request is None:
            return None
        flag = next(
            (d for d in request.decisions.all() if d.decision == ReviewDecisionType.REJECT), None
        )
        return flag.reason if flag else None


class DocumentResource(serializers.ModelSerializer):
    unit_id = serializers.IntegerField(source="property_unit_id")
    versions = DocumentVersionResource(many=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "document_type",
            "unit_id",
            "tenancy_id",
            "maintenance_issue_id",
            "current_version_id",
            "versions",
        ]
