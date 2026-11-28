from rest_framework import serializers

from reviews.models import ReviewDecisionType, ReviewRequest, ReviewStatus


class DocumentCaseResource(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=[ReviewStatus.PENDING_REVIEW, ReviewStatus.APPROVED, ReviewStatus.REJECTED]
    )
    document_id = serializers.SerializerMethodField()
    tenancy_id = serializers.SerializerMethodField()
    version_id = serializers.SerializerMethodField()
    version_no = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    raised_by_name = serializers.SerializerMethodField()
    raised_by_side = serializers.CharField(source="requester_side")
    reason = serializers.CharField(source="dispute.details")
    flag_reason = serializers.SerializerMethodField(
        help_text="What the tenant said was wrong, when the version was flagged."
    )
    decision_reason = serializers.SerializerMethodField(
        help_text="The admin's reason once the case is decided."
    )

    class Meta:
        model = ReviewRequest
        fields = [
            "id",
            "status",
            "document_id",
            "tenancy_id",
            "version_id",
            "version_no",
            "title",
            "raised_by_name",
            "raised_by_side",
            "reason",
            "flag_reason",
            "decision_reason",
            "submitted_at",
        ]

    def _version(self, case):
        return case.parent_request.current_submission.proposed_document_version

    def get_document_id(self, case) -> int:
        return self._version(case).document_id

    def get_tenancy_id(self, case) -> int | None:
        return self._version(case).document.tenancy_id

    def get_version_id(self, case) -> int:
        return self._version(case).pk

    def get_version_no(self, case) -> int:
        return self._version(case).version_no

    def get_title(self, case) -> str:
        return self._version(case).title

    def get_raised_by_name(self, case) -> str:
        return f"{case.requested_by.first_name} {case.requested_by.last_name}"

    def get_flag_reason(self, case) -> str | None:
        flag = next(
            (
                d
                for d in case.parent_request.decisions.all()
                if d.decision == ReviewDecisionType.REJECT
            ),
            None,
        )
        return flag.reason if flag else None

    def get_decision_reason(self, case) -> str | None:
        answer = next(iter(case.decisions.all()), None)
        return answer.reason if answer else None


class DocumentCasePageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = DocumentCaseResource(many=True)
