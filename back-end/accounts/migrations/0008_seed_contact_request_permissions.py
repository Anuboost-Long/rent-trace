from django.db import migrations

# Frozen: tenants ask a landlord for contact; landlords answer.
NEW_PERMISSIONS = [
    ("contact_requests.send", "Ask a landlord for contact", "communications", "TENANT"),
    ("contact_requests.respond", "Answer contact requests", "communications", "LANDLORD"),
]


def seed(apps, _schema_editor):
    Role = apps.get_model("accounts", "Role")
    Permission = apps.get_model("accounts", "Permission")
    RolePermissionBridge = apps.get_model("accounts", "RolePermissionBridge")
    for code, name, module, role_code in NEW_PERMISSIONS:
        permission, _ = Permission.objects.update_or_create(
            code=code, defaults={"name": name, "module": module, "is_admin_only": False}
        )
        RolePermissionBridge.objects.get_or_create(
            role=Role.objects.get(code=role_code), permission=permission
        )


def unseed(apps, _schema_editor):
    codes = [code for code, *_ in NEW_PERMISSIONS]
    apps.get_model("accounts", "RolePermissionBridge").objects.filter(
        permission__code__in=codes
    ).delete()
    apps.get_model("accounts", "Permission").objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):
    dependencies = [("accounts", "0007_seed_tenancy_permissions")]

    operations = [migrations.RunPython(seed, unseed)]
