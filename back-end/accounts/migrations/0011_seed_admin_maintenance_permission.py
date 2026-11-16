from django.db import migrations

# Frozen: admins read every maintenance issue, across landlords.
NEW_PERMISSIONS = [
    ("maintenance.admin_view", "View maintenance issues as an admin", "maintenance"),
]


def seed(apps, _schema_editor):
    Role = apps.get_model("accounts", "Role")
    Permission = apps.get_model("accounts", "Permission")
    RolePermissionBridge = apps.get_model("accounts", "RolePermissionBridge")
    for code, name, module in NEW_PERMISSIONS:
        permission, _ = Permission.objects.update_or_create(
            code=code, defaults={"name": name, "module": module, "is_admin_only": True}
        )
        RolePermissionBridge.objects.get_or_create(
            role=Role.objects.get(code="ADMIN"), permission=permission
        )


def unseed(apps, _schema_editor):
    codes = [code for code, *_ in NEW_PERMISSIONS]
    apps.get_model("accounts", "RolePermissionBridge").objects.filter(
        permission__code__in=codes
    ).delete()
    apps.get_model("accounts", "Permission").objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):
    dependencies = [("accounts", "0010_seed_terms_permission")]

    operations = [migrations.RunPython(seed, unseed)]
