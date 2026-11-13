from rest_framework import serializers

from common.models import PartySide
from maintenance.resources.issue_summary import IssueSummaryResource, _name
from maintenance.services.shared.actions import allowed_actions
from maintenance.services.shared.parties import side_of
from providers.models import PropertyServiceProvider


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
    assignment = serializers.SerializerMethodField(
        help_text="The tradesperson booked now, with their contact details."
    )
    provider_options = serializers.SerializerMethodField(
        help_text="Landlord only: tradespeople linked to this property, preferred and matching first."
    )

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
            "assignment",
            "provider_options",
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
        entries = [
            {
                "kind": "STATUS",
                "from_status": row.from_status,
                "to_status": row.to_status,
                "trigger": row.trigger,
                "actor": _name(row.actor),
                "reason": row.reason,
                "created_at": row.created_at,
            }
            for row in rows
        ]
        return sorted(
            [*entries, *self._visit_entries(issue)], key=lambda entry: entry["created_at"]
        )

    def _visit_entries(self, issue) -> list[dict]:
        entries = []
        bookings = issue.assignments.select_related("service_provider", "recorded_by")
        for booking in bookings.order_by("id"):
            provider = booking.service_provider.business_name
            entries.append(_visit_entry("PROVIDER_BOOKED", booking, booking.created_at, provider))
            if booking.completed_at is not None:
                entries.append(_visit_entry("VISIT_DONE", booking, booking.completed_at, provider))
        return entries

    def get_actions(self, issue) -> list[str]:
        return allowed_actions(issue, self.context["user"])

    def get_my_side(self, issue) -> str | None:
        return side_of(self.context["user"], issue)

    def get_assignment(self, issue) -> dict | None:
        current = (
            issue.assignments.filter(superseded_by__isnull=True)
            .select_related("service_provider")
            .first()
        )
        if current is None:
            return None
        provider = current.service_provider
        categories = provider.categories.filter(deleted_at__isnull=True).select_related(
            "service_category"
        )
        return {
            "id": current.pk,
            "scheduled_at": current.scheduled_at,
            "completed_at": current.completed_at,
            "created_at": current.created_at,
            "provider": {
                "id": provider.pk,
                "business_name": provider.business_name,
                "contact_name": provider.contact_name,
                "phone_number": provider.phone_number,
                "email": provider.email,
                "website": provider.website,
                "address": provider.address,
                "description": provider.description,
                "categories": [
                    {"code": row.service_category.code, "name": row.service_category.name}
                    for row in categories.order_by("service_category__name")
                ],
            },
        }

    def get_provider_options(self, issue) -> list[dict]:
        if side_of(self.context["user"], issue) != PartySide.LANDLORD:
            return []
        links = PropertyServiceProvider.objects.filter(
            property=issue.property_unit.property_id,
            service_provider__owner=self.context["user"],
            service_provider__deleted_at__isnull=True,
            deleted_at__isnull=True,
        ).select_related("service_provider")
        wanted = issue.service_category_id
        options = [
            {
                "id": link.service_provider_id,
                "business_name": link.service_provider.business_name,
                "is_recommended": link.is_recommended,
                "matches_category": bool(wanted)
                and link.service_provider.categories.filter(
                    service_category_id=wanted, deleted_at__isnull=True
                ).exists(),
            }
            for link in links
        ]
        return sorted(
            options,
            key=lambda row: (
                not row["matches_category"],
                not row["is_recommended"],
                row["business_name"],
            ),
        )


def _visit_entry(kind, booking, created_at, provider) -> dict:
    return {
        "kind": kind,
        "from_status": None,
        "to_status": None,
        "trigger": kind,
        "actor": _name(booking.recorded_by),
        "reason": provider,
        "created_at": created_at,
    }
