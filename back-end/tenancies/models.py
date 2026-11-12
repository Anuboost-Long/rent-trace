from django.db import models
from django.db.models import Count, F, Prefetch, Q
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


class TenancyQuerySet(models.QuerySet):
    def live(self):
        return self.filter(deleted_at__isnull=True)

    def in_properties(self, properties):
        return self.filter(property_unit__property__in=properties)

    def with_status(self, status):
        return self.filter(status=status)

    def overlapping(self, start, end):
        others = self.filter(Q(end_date__isnull=True) | Q(end_date__gt=start))
        return others.filter(start_date__lt=end) if end else others

    def for_tenant(self, user):
        joined = TenancyParty.objects.filter(tenant=user, deleted_at__isnull=True)
        return self.filter(pk__in=joined.values("tenancy_id"))

    def search(self, text):
        matches = self
        for term in text.split():
            tenant_matches = TenancyParty.objects.current().filter(
                Q(tenant__email__icontains=term)
                | Q(tenant__first_name__icontains=term)
                | Q(tenant__last_name__icontains=term)
            )
            matches = matches.filter(
                Q(reference_no__icontains=term)
                | Q(property_unit__name__icontains=term)
                | Q(property_unit__property__property_name__icontains=term)
                | Q(property_unit__property__address_line_1__icontains=term)
                | Q(property_unit__property__suburb__icontains=term)
                | Q(pk__in=tenant_matches.values("tenancy_id"))
            )
        return matches

    def status_counts(self):
        rows = self.order_by().values("status").annotate(total=Count("id"))
        return {row["status"]: row["total"] for row in rows}

    def ending_between(self, first_day, last_day):
        return self.filter(end_date__gte=first_day, end_date__lte=last_day)

    def newest_first(self):
        return self.order_by("-created_at", "-id")

    def with_parties_and_invitations(self):
        return self.select_related("property_unit__property").prefetch_related(
            Prefetch(
                "parties",
                queryset=TenancyParty.objects.current().select_related("tenant").order_by("id"),
                to_attr="current_parties",
            ),
            Prefetch(
                "invitations",
                queryset=TenancyInvitation.objects.not_deleted().order_by("-id"),
                to_attr="all_invitations",
            ),
        )


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

    objects = TenancyQuerySet.as_manager()

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


class TenancyPartyQuerySet(models.QuerySet):
    def current(self):
        return self.filter(left_at__isnull=True, deleted_at__isnull=True)

    def primary(self):
        return self.filter(is_primary=True)

    def with_tenant_email(self, email_normalized):
        return self.filter(tenant__email_normalized=email_normalized)


class TenancyParty(MutableRecord):
    tenancy = models.ForeignKey(Tenancy, models.PROTECT, related_name="parties")
    tenant = models.ForeignKey("accounts.User", models.PROTECT, related_name="tenancy_memberships")
    is_primary = models.BooleanField(default=False)
    joined_at = models.DateField()
    left_at = models.DateField(null=True, blank=True)

    objects = TenancyPartyQuerySet.as_manager()

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
                condition=Q(left_at__isnull=True, deleted_at__isnull=True),
                name="uq_current_tenancy_party",
            ),
            models.UniqueConstraint(
                fields=["tenancy"],
                condition=Q(is_primary=True, left_at__isnull=True, deleted_at__isnull=True),
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


class TenancyInvitationQuerySet(models.QuerySet):
    def not_deleted(self):
        return self.filter(deleted_at__isnull=True)

    def outstanding(self):
        return self.not_deleted().filter(accepted_at__isnull=True, revoked_at__isnull=True)

    def pending(self, now):
        return self.outstanding().filter(expires_at__gt=now)

    def expired(self, now):
        return self.outstanding().filter(expires_at__lte=now)

    def with_email(self, email_normalized):
        return self.filter(email_normalized=email_normalized)

    def matching(self, token_hash):
        return self.filter(token_hash=token_hash)


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

    objects = TenancyInvitationQuerySet.as_manager()

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
                condition=Q(
                    accepted_at__isnull=True, revoked_at__isnull=True, deleted_at__isnull=True
                ),
                name="uq_tenancy_invitations_pending",
            ),
        ]
        indexes = [
            models.Index(fields=["email_normalized"], name="ix_tenancy_invitations_email"),
        ]
