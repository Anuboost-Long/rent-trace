from django.db import models
from django.db.models import Q
from django.db.models.functions import Trim
from django.db.models.lookups import Exact


class PartySide(models.TextChoices):
    LANDLORD = "LANDLORD"
    TENANT = "TENANT"


def enum_check(table, field, choices):
    return models.CheckConstraint(
        condition=Q(**{f"{field}__in": choices.values}),
        name=f"ck_{table}_{field}",
    )


def nonblank_check(table, field):
    return models.CheckConstraint(
        condition=~Q(Exact(Trim(field), "")),
        name=f"ck_{table}_{field}_nonblank",
    )


class MutableRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "accounts.User", models.PROTECT, null=True, blank=True, related_name="+"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        "accounts.User", models.PROTECT, null=True, blank=True, related_name="+"
    )
    row_version = models.PositiveBigIntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        "accounts.User", models.PROTECT, null=True, blank=True, related_name="+"
    )

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                condition=Q(row_version__gte=1),
                name="ck_%(app_label)s_%(class)s_row_version",
            ),
            models.CheckConstraint(
                condition=Q(is_deleted=True, deleted_at__isnull=False)
                | Q(is_deleted=False, deleted_at__isnull=True),
                name="ck_%(app_label)s_%(class)s_deleted_at",
            ),
        ]


class EventRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "accounts.User", models.PROTECT, null=True, blank=True, related_name="+"
    )
    correlation_id = models.UUIDField()

    class Meta:
        abstract = True


class CatalogueRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class LinkRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", models.PROTECT, related_name="+")

    class Meta:
        abstract = True
