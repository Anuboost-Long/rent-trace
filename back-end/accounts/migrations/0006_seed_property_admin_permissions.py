from django.db import migrations

# Frozen: the permissions an admin needs to set up properties for landlords.
NEW_PERMISSIONS = [
    ("properties.admin_view", "View properties as an admin", "properties"),
    ("properties.admin_manage", "Set up and edit properties for landlords", "properties"),
]


def seed(apps, _schema_editor):
    Role = apps.get_model("accounts", "Role")
    Permission = apps.get_model("accounts", "Permission")
    RolePermissionBridge = apps.get_model("accounts", "RolePermissionBridge")
    admin = Role.objects.get(code="ADMIN")
    for code, name, module in NEW_PERMISSIONS:
        permission, _ = Permission.objects.update_or_create(
            code=code, defaults={"name": name, "module": module, "is_admin_only": True}
        )
        RolePermissionBridge.objects.get_or_create(role=admin, permission=permission)


def unseed(apps, _schema_editor):
    codes = [code for code, _, _ in NEW_PERMISSIONS]
    apps.get_model("accounts", "RolePermissionBridge").objects.filter(
        permission__code__in=codes
    ).delete()
    apps.get_model("accounts", "Permission").objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):
    dependencies = [("accounts", "0005_seed_ban_and_token_permissions")]

    operations = [migrations.RunPython(seed, unseed)]
