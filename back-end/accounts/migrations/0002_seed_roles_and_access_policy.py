from django.db import migrations

ROLES = [
    ("ADMIN", "Admin", "Operational authority: reviews Admin-routed cases and manages access."),
    ("LANDLORD", "Landlord", "Owns properties and manages their tenancies."),
    ("TENANT", "Tenant", "Rents a unit or area under a tenancy."),
]


def seed(apps, _schema_editor):
    Role = apps.get_model("accounts", "Role")
    AccessPolicy = apps.get_model("accounts", "AccessPolicy")
    for code, name, description in ROLES:
        Role.objects.update_or_create(code=code, defaults={"name": name, "description": description})
    AccessPolicy.objects.get_or_create(id=1, defaults={"hidden_records_mode": "DENY_ALL"})


def unseed(apps, _schema_editor):
    apps.get_model("accounts", "AccessPolicy").objects.filter(id=1).delete()
    apps.get_model("accounts", "Role").objects.filter(code__in=[code for code, _, _ in ROLES]).delete()


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]

    operations = [migrations.RunPython(seed, unseed)]
