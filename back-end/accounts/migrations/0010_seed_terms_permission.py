from django.db import migrations

# Frozen: tenants approve or decline a rent or bond increase their landlord proposes.
NEW_PERMISSIONS = [
    (
        "tenancies.approve_terms",
        "Approve or decline a rent or bond increase",
        "tenancies",
        "TENANT",
        False,
    ),
]


def seed(apps, _schema_editor):
    Role = apps.get_model("accounts", "Role")
    Permission = apps.get_model("accounts", "Permission")
    RolePermissionBridge = apps.get_model("accounts", "RolePermissionBridge")
    for code, name, module, role_code, is_admin_only in NEW_PERMISSIONS:
        permission, _ = Permission.objects.update_or_create(
            code=code,
            defaults={"name": name, "module": module, "is_admin_only": is_admin_only},
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
    dependencies = [("accounts", "0009_seed_housemate_permission")]

    operations = [migrations.RunPython(seed, unseed)]
