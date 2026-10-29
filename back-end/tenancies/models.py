from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower, Trim

from common.models import MutableRecord, enum_check


class TenancyType(models.TextChoices):
    WHOLE_UNIT = "WHOLE_UNIT"
    AREA_BASED = "AREA_BASED"


class TenancyStatus(models.TextChoices):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"


class Tenancy(MutableRecord):
    property_unit = models.ForeignKey(
        "properties.PropertyUnit", models.PROTECT, related_name="tenancies"
    )
    reference_no = models.CharField(max_length=50, unique=True)
    tenancy_type = models.TextField(choices=TenancyType)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.TextField(choices=TenancyStatus, default=TenancyStatus.DRAFT)
    rent_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rent_frequency = models.CharField(max_length=30, null=True, blank=True)
    bond_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="AUD")
    notes = models.TextField(null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "tenancies"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("tenancies", "tenancy_type", TenancyType),
            enum_check("tenancies", "status", TenancyStatus),
            models.CheckConstraint(
                condition=Q(end_date__isnull=True) | Q(end_date__gt=F("start_date")),
                name="ck_tenancies_dates",
            ),
            models.CheckConstraint(
                condition=Q(rent_amount__gte=0), name="ck_tenancies_rent_amount"
            ),
            models.CheckConstraint(
                condition=Q(bond_amount__gte=0), name="ck_tenancies_bond_amount"
            ),
        ]
        indexes = [
            models.Index(
                fields=["property_unit", "status", "start_date", "end_date"],
                name="ix_tenancies_unit_period",
            ),
        ]


class TenancyParty(MutableRecord):
    tenancy = models.ForeignKey(Tenancy, models.PROTECT, related_name="parties")
    tenant = models.ForeignKey("accounts.User", models.PROTECT, related_name="tenancy_memberships")
    is_primary = models.BooleanField(default=False)
    joined_at = models.DateField()
    left_at = models.DateField(null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "tenancy_parties"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.CheckConstraint(
                condition=Q(left_at__isnull=True) | Q(left_at__gt=F("joined_at")),
                name="ck_tenancy_parties_interval",
            ),
            models.UniqueConstraint(
                fields=["tenancy", "tenant"],
                condition=Q(left_at__isnull=True, is_deleted=False),
                name="uq_current_tenancy_party",
            ),
            models.UniqueConstraint(
                fields=["tenancy"],
                condition=Q(is_primary=True, left_at__isnull=True, is_deleted=False),
                name="uq_current_primary_tenant",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "tenancy"], name="ix_tenancy_parties_tenant"),
        ]


class TenancyArea(MutableRecord):
    tenancy = models.ForeignKey(Tenancy, models.PROTECT, related_name="areas")
    unit_area = models.ForeignKey(
        "properties.UnitArea", models.PROTECT, related_name="tenancy_areas"
    )

    class Meta(MutableRecord.Meta):
        db_table = "tenancy_areas"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.UniqueConstraint(fields=["tenancy", "unit_area"], name="uq_tenancy_areas"),
        ]


class TenancyInvitation(MutableRecord):
    tenancy = models.ForeignKey(Tenancy, models.PROTECT, related_name="invitations")
    email_normalized = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(
        "accounts.User", models.PROTECT, null=True, blank=True, related_name="accepted_invitations"
    )
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "tenancy_invitations"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.CheckConstraint(
                condition=Q(email_normalized=Lower(Trim("email_normalized"))),
                name="ck_tenancy_invitations_email_normalized",
            ),
            models.CheckConstraint(
                condition=Q(expires_at__gt=F("created_at")),
                name="ck_tenancy_invitations_expiry",
            ),
            models.CheckConstraint(
                condition=Q(accepted_at__isnull=True, accepted_by__isnull=True)
                | Q(accepted_at__isnull=False, accepted_by__isnull=False),
                name="ck_tenancy_invitations_accepted",
            ),
            models.CheckConstraint(
                condition=Q(accepted_at__isnull=True) | Q(revoked_at__isnull=True),
                name="ck_tenancy_invitations_outcome",
            ),
            models.UniqueConstraint(
                fields=["tenancy", "email_normalized"],
                condition=Q(accepted_at__isnull=True, revoked_at__isnull=True, is_deleted=False),
                name="uq_tenancy_invitations_pending",
            ),
        ]
        indexes = [
            models.Index(fields=["email_normalized"], name="ix_tenancy_invitations_email"),
        ]
