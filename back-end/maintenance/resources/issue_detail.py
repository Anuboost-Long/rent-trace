from rest_framework import serializers

from maintenance.resources.issue_summary import IssueSummaryResource, _name
from maintenance.services.shared.actions import allowed_actions
from maintenance.services.shared.parties import side_of


class IssueDetailResource(IssueSummaryResource):
    """Needs `user` in the context: what the person can do depends on who they are."""

    description = serializers.CharField()
    open_closure = serializers.SerializerMethodField(
        help_text="The proposal waiting for an answer."
    )
    history = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField(
        help_text="What the signed-in person can do now: ACKNOWLEDGE, START, PROPOSE_CLOSURE, "
        "WITHDRAW_CLOSURE, APPROVE_CLOSURE, REJECT_CLOSURE or CLOSE_VACANT."
    )
    my_side = serializers.SerializerMethodField()

    class Meta(IssueSummaryResource.Meta):
        fields = [
            *IssueSummaryResource.Meta.fields,
            "description",
            "acknowledged_at",
            "work_started_at",
            "open_closure",
            "history",
            "actions",
            "my_side",
        ]

    def get_open_closure(self, issue) -> dict | None:
        proposal = issue.open_closure_proposal
        if proposal is None:
            return None
        return {
            "id": proposal.pk,
            "outcome": proposal.outcome,
            "reason": proposal.reason,
            "proposed_by": _name(proposal.proposed_by),
            "proposer_side": proposal.proposer_side,
            "created_at": proposal.created_at,
        }

    def get_history(self, issue) -> list[dict]:
        rows = issue.status_history.select_related("actor").order_by("sequence_no")
        return [
            {
                "sequence_no": row.sequence_no,
                "from_status": row.from_status,
                "to_status": row.to_status,
                "trigger": row.trigger,
                "actor": _name(row.actor),
                "reason": row.reason,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    def get_actions(self, issue) -> list[str]:
        return allowed_actions(issue, self.context["user"])

    def get_my_side(self, issue) -> str | None:
        return side_of(self.context["user"], issue)
