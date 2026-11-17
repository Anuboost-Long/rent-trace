from django.db import migrations

CATEGORIES = [
    ("PLUMBING", "Plumbing"),
    ("ELECTRICAL", "Electrical"),
    ("APPLIANCES", "Appliances"),
    ("HEATING_COOLING", "Heating and cooling"),
    ("LOCKS_DOORS", "Locks and doors"),
    ("PESTS", "Pest control"),
    ("GENERAL", "General repairs"),
]


def seed(apps, _schema_editor):
    ServiceCategory = apps.get_model("providers", "ServiceCategory")
    for code, name in CATEGORIES:
        ServiceCategory.objects.update_or_create(code=code, defaults={"name": name})


def unseed(apps, _schema_editor):
    apps.get_model("providers", "ServiceCategory").objects.filter(
        code__in=[code for code, _ in CATEGORIES]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("providers", "0002_provider_owner")]

    operations = [migrations.RunPython(seed, unseed)]
