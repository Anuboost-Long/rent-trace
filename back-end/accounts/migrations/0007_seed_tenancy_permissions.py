from django.db import migrations

# Frozen: admin access to tenancies, and the tenant's right to accept an invitation.
NEW_PERMISSIONS = [
    ("tenancies.admin_view", "View tenancies as an admin", "tenancies", "ADMIN", True),
    ("tenancies.admin_manage", "Set up tenancies and invite tenants", "tenancies", "ADMIN", True),
    ("tenancies.accept_invitation", "Accept a tenancy invitation", "tenancies", "TENANT", False),
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
    dependencies = [("accounts", "0006_seed_property_admin_permissions")]

    operations = [migrations.RunPython(seed, unseed)]
