from django.db import models
from django.db.models import Case, Value, When
from django.db.models.lookups import Exact

from common.models import EventRecord

TARGET_FIELDS = [
    "property",
    "property_unit",
    "unit_area",
    "tenancy",
    "condition_record",
    "maintenance_issue",
    "document",
    "communication_log",
    "property_service_provider",
    "user",
    "file",
    "access_policy",
]

def target_link(model):
    return models.OneToOneField(
        model, models.PROTECT, null=True, blank=True, related_name="review_target"
    )


class ReviewTarget(EventRecord):
    property = target_link("properties.Property")
    property_unit = target_link("properties.PropertyUnit")
    unit_area = target_link("properties.UnitArea")
    tenancy = target_link("tenancies.Tenancy")
    condition_record = target_link("conditions.ConditionRecord")
    maintenance_issue = target_link("maintenance.MaintenanceIssue")
    document = target_link("documents.Document")
    communication_log = target_link("communications.CommunicationLog")
    property_service_provider = target_link("providers.PropertyServiceProvider")
    user = target_link("accounts.User")
    file = target_link("files.File")
    access_policy = target_link("accounts.AccessPolicy")

    class Meta:
        db_table = "review_targets"
        constraints = [
            models.CheckConstraint(
                condition=Exact(
                    sum(
                        (
                            Case(When(**{f"{field}__isnull": False}, then=1), default=0)
                            for field in TARGET_FIELDS
                        ),
                        Value(0),
                    ),
                    1,
                ),
                name="ck_review_targets_exactly_one",
            ),
        ]
