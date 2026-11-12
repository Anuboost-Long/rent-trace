from rest_framework import serializers

from maintenance.models import MaintenanceIssue


def _name(person):
    return f"{person.first_name} {person.last_name}"


class IssueSummaryResource(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    property = serializers.SerializerMethodField()
    reported_by_name = serializers.SerializerMethodField()
    has_open_closure = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceIssue
        fields = [
            "id",
            "title",
            "priority",
            "status",
            "reported_at",
            "closed_at",
            "closure_outcome",
            "unit",
            "property",
            "reported_by_name",
            "has_open_closure",
        ]

    def get_unit(self, issue) -> dict:
        unit = issue.property_unit
        return {"id": unit.pk, "name": unit.name}

    def get_property(self, issue) -> dict:
        place = issue.property_unit.property
        return {"id": place.pk, "name": place.property_name, "suburb": place.suburb}

    def get_reported_by_name(self, issue) -> str:
        return _name(issue.reported_by)

    def get_has_open_closure(self, issue) -> bool:
        return issue.open_closure_proposal_id is not None
