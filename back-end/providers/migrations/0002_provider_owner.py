import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q
from django.db.models.functions import Trim
from django.db.models.lookups import Exact


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("providers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceprovider",
            name="owner",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="service_providers",
                to="accounts.user",
            ),
        ),
        migrations.RemoveField(model_name="serviceprovider", name="property"),
        migrations.AlterField(
            model_name="serviceprovider",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="service_providers",
                to="accounts.user",
            ),
        ),
        migrations.AddConstraint(
            model_name="serviceprovider",
            constraint=models.CheckConstraint(
                condition=~Q(Exact(Trim("business_name"), "")),
                name="ck_service_providers_business_name_nonblank",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="serviceprovidercategory", name="uq_service_provider_categories"
        ),
        migrations.AddConstraint(
            model_name="serviceprovidercategory",
            constraint=models.UniqueConstraint(
                condition=Q(deleted_at__isnull=True),
                fields=("service_provider", "service_category"),
                name="uq_service_provider_categories",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="propertyserviceprovider", name="uq_property_service_providers"
        ),
        migrations.AddConstraint(
            model_name="propertyserviceprovider",
            constraint=models.UniqueConstraint(
                condition=Q(deleted_at__isnull=True),
                fields=("property", "service_provider"),
                name="uq_property_service_providers",
            ),
        ),
    ]
