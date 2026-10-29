from django.db import models
from django.db.models import Q

from common.models import CatalogueRecord, EventRecord, MutableRecord


class ServiceCategory(CatalogueRecord):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "service_categories"


class ServiceProvider(MutableRecord):
    property = models.ForeignKey(
        "properties.Property", models.PROTECT, related_name="service_providers"
    )
    business_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    website = models.URLField(max_length=500, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "service_providers"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.CheckConstraint(
                condition=Q(phone_number__isnull=False)
                | Q(email__isnull=False)
                | Q(website__isnull=False),
                name="ck_service_providers_contact",
            ),
        ]


class ServiceProviderCategory(MutableRecord):
    service_provider = models.ForeignKey(ServiceProvider, models.PROTECT, related_name="categories")
    service_category = models.ForeignKey(ServiceCategory, models.PROTECT, related_name="providers")

    class Meta(MutableRecord.Meta):
        db_table = "service_provider_categories"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.UniqueConstraint(
                fields=["service_provider", "service_category"],
                name="uq_service_provider_categories",
            ),
        ]


class PropertyServiceProvider(MutableRecord):
    property = models.ForeignKey(
        "properties.Property", models.PROTECT, related_name="provider_links"
    )
    service_provider = models.ForeignKey(
        ServiceProvider, models.PROTECT, related_name="property_links"
    )
    is_recommended = models.BooleanField(default=False)
    contract_notes = models.TextField(null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "property_service_providers"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.UniqueConstraint(
                fields=["property", "service_provider"],
                name="uq_property_service_providers",
            ),
        ]


class MaintenanceAssignment(EventRecord):
    maintenance_issue = models.ForeignKey(
        "maintenance.MaintenanceIssue", models.PROTECT, related_name="assignments"
    )
    service_provider = models.ForeignKey(
        ServiceProvider, models.PROTECT, related_name="assignments"
    )
    supersedes_assignment = models.ForeignKey(
        "self", models.PROTECT, null=True, blank=True, related_name="superseded_by"
    )
    recorded_by = models.ForeignKey(
        "accounts.User", models.PROTECT, related_name="recorded_assignments"
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "maintenance_assignments"
