from django.db import models
from django.db.models import F, Q

from common.models import MutableRecord, enum_check


class PropertyStatus(models.TextChoices):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    ARCHIVED = "ARCHIVED"


class ListingStatus(models.TextChoices):
    DRAFT = "DRAFT"
    AVAILABLE = "AVAILABLE"
    PARTIALLY_AVAILABLE = "PARTIALLY_AVAILABLE"
    FULLY_OCCUPIED = "FULLY_OCCUPIED"
    UNLISTED = "UNLISTED"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


class Property(MutableRecord):
    property_name = models.CharField(max_length=150, null=True, blank=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    suburb = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="Australia")
    property_type = models.CharField(max_length=50)
    property_status = models.TextField(choices=PropertyStatus, default=PropertyStatus.ACTIVE)
    listing_status = models.TextField(choices=ListingStatus, default=ListingStatus.DRAFT)
    public_description = models.TextField(null=True, blank=True)
    private_notes = models.TextField(null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "properties"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("properties", "property_status", PropertyStatus),
            enum_check("properties", "listing_status", ListingStatus),
        ]
        indexes = [
            models.Index(fields=["listing_status", "deleted_at"], name="ix_properties_listing"),
        ]


class PropertyOwner(MutableRecord):
    property = models.ForeignKey(Property, models.PROTECT, related_name="owners")
    owner = models.ForeignKey("accounts.User", models.PROTECT, related_name="property_ownerships")
    is_primary_owner = models.BooleanField(default=False)
    ownership_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "property_owners"
        constraints = [
            *MutableRecord.Meta.constraints,
            models.CheckConstraint(
                condition=Q(ownership_percentage__gt=0, ownership_percentage__lte=100),
                name="ck_property_owners_percentage",
            ),
            models.CheckConstraint(
                condition=Q(valid_to__isnull=True) | Q(valid_to__gt=F("valid_from")),
                name="ck_property_owners_interval",
            ),
            models.UniqueConstraint(
                fields=["property", "owner"],
                condition=Q(valid_to__isnull=True, deleted_at__isnull=True),
                name="uq_current_property_owner",
            ),
            models.UniqueConstraint(
                fields=["property"],
                condition=Q(is_primary_owner=True, valid_to__isnull=True, deleted_at__isnull=True),
                name="uq_current_primary_owner",
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "property"], name="ix_property_owners_owner"),
        ]


class OccupancyStatus(models.TextChoices):
    VACANT = "VACANT"
    PARTIALLY_OCCUPIED = "PARTIALLY_OCCUPIED"
    OCCUPIED = "OCCUPIED"
    UNAVAILABLE = "UNAVAILABLE"


class RentFrequency(models.TextChoices):
    WEEKLY = "WEEKLY"
    FORTNIGHTLY = "FORTNIGHTLY"
    MONTHLY = "MONTHLY"


class PropertyUnit(MutableRecord):
    property = models.ForeignKey(Property, models.PROTECT, related_name="units")
    name = models.CharField(max_length=150)
    unit_number = models.CharField(max_length=50, null=True, blank=True)
    unit_type = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    occupancy_status = models.TextField(choices=OccupancyStatus, default=OccupancyStatus.VACANT)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rent_frequency = models.TextField(choices=RentFrequency, null=True, blank=True)

    class Meta(MutableRecord.Meta):
        db_table = "property_units"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("property_units", "occupancy_status", OccupancyStatus),
            enum_check("property_units", "rent_frequency", RentFrequency),
            models.CheckConstraint(
                condition=Q(rent_amount__isnull=True) | Q(rent_amount__gt=0),
                name="ck_property_units_rent_positive",
            ),
            models.CheckConstraint(
                condition=(Q(rent_amount__isnull=True) & Q(rent_frequency__isnull=True))
                | (Q(rent_amount__isnull=False) & Q(rent_frequency__isnull=False)),
                name="ck_property_units_rent_pair",
            ),
        ]


class UnitArea(MutableRecord):
    property_unit = models.ForeignKey(PropertyUnit, models.PROTECT, related_name="areas")
    name = models.CharField(max_length=100)
    area_type = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta(MutableRecord.Meta):
        db_table = "unit_areas"


class PropertyFileKind(models.TextChoices):
    PHOTO = "PHOTO"
    DOCUMENT = "DOCUMENT"


class PropertyFile(MutableRecord):
    property = models.ForeignKey(Property, models.PROTECT, related_name="files")
    property_unit = models.ForeignKey(
        PropertyUnit, models.PROTECT, null=True, blank=True, related_name="files"
    )
    file = models.OneToOneField("files.File", models.PROTECT, related_name="property_file")
    kind = models.TextField(choices=PropertyFileKind)
    caption = models.CharField(max_length=200, null=True, blank=True)
    is_cover = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta(MutableRecord.Meta):
        db_table = "property_files"
        constraints = [
            *MutableRecord.Meta.constraints,
            enum_check("property_files", "kind", PropertyFileKind),
            models.CheckConstraint(
                condition=Q(is_cover=False) | Q(kind=PropertyFileKind.PHOTO),
                name="ck_property_files_cover_is_photo",
            ),
            models.UniqueConstraint(
                fields=["property"],
                condition=Q(is_cover=True, deleted_at__isnull=True, property_unit__isnull=True),
                name="uq_property_files_one_cover",
            ),
            models.UniqueConstraint(
                fields=["property_unit"],
                condition=Q(is_cover=True, deleted_at__isnull=True, property_unit__isnull=False),
                name="uq_property_files_one_unit_cover",
            ),
        ]
        indexes = [
            models.Index(
                fields=["property", "property_unit", "kind"], name="ix_property_files_scope"
            )
        ]
