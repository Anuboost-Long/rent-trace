from django.utils import timezone
from rest_framework import serializers

from tenancies.models import TenancyTermChange, TermChangeStatus


def _money(amount):
    return None if amount is None else f"{amount:.2f}"


def _terms(rent_amount, rent_frequency, bond_amount) -> dict:
    return {
        "rent_amount": _money(rent_amount),
        "rent_frequency": rent_frequency,
        "bond_amount": _money(bond_amount),
    }


class TermChangeResource(serializers.ModelSerializer):
    """A rent or bond change: waiting for approval, applied, declined or withdrawn.

    Pass `people` (the current tenants as {user_id, name}) in the context to list who has answered.
    """

    status = serializers.SerializerMethodField(
        help_text="PENDING turns into EXPIRED after 14 days."
    )
    proposed_by = serializers.SerializerMethodField()
    before = serializers.SerializerMethodField()
    after = serializers.SerializerMethodField()
    approvals = serializers.SerializerMethodField(
        help_text="Each current tenant and their answer (APPROVED, DECLINED or null)."
    )

    class Meta:
        model = TenancyTermChange
        fields = [
            "id",
            "status",
            "requires_approval",
            "proposed_by",
            "created_at",
            "decided_at",
            "expires_at",
            "before",
            "after",
            "approvals",
        ]

    def get_status(self, change) -> str:
        expired = change.status == TermChangeStatus.PENDING and change.expires_at <= timezone.now()
        return "EXPIRED" if expired else change.status

    def get_proposed_by(self, change) -> str | None:
        asker = change.created_by
        return f"{asker.first_name} {asker.last_name}" if asker else None

    def get_before(self, change) -> dict:
        return _terms(change.from_rent_amount, change.from_rent_frequency, change.from_bond_amount)

    def get_after(self, change) -> dict:
        return _terms(change.rent_amount, change.rent_frequency, change.bond_amount)

    def get_approvals(self, change) -> list[dict]:
        if change.status != TermChangeStatus.PENDING:
            return []
        answers = {row.tenant_id: row.decision for row in change.decisions.all()}
        return [
            {"name": person["name"], "decision": answers.get(person["user_id"])}
            for person in self.context.get("people", [])
        ]


class MyTermChangeResource(TermChangeResource):
    my_decision = serializers.SerializerMethodField()

    class Meta(TermChangeResource.Meta):
        fields = [*TermChangeResource.Meta.fields, "my_decision"]

    def get_my_decision(self, change) -> str | None:
        me = self.context.get("me_id")
        return next((row.decision for row in change.decisions.all() if row.tenant_id == me), None)
