from django.db import migrations

# Frozen copy of accounts/seeds/permissions.py at the time of this migration.
PERMISSIONS = [
    ("accounts.update_profile", "Update own profile", "accounts", ["ADMIN", "LANDLORD", "TENANT"]),
    ("accounts.view", "View user accounts", "accounts", ["ADMIN"]),
    ("accounts.create", "Create user accounts", "accounts", ["ADMIN"]),
    ("accounts.update", "Edit user accounts", "accounts", ["ADMIN"]),
    ("accounts.manage", "Suspend and reactivate accounts", "accounts", ["ADMIN"]),
    ("accounts.delete", "Delete user accounts", "accounts", ["ADMIN"]),
    ("access.manage", "Grant and revoke roles and permissions", "access", ["ADMIN"]),
    ("access.view_hidden_records", "View hidden records", "access", []),
    (
        "properties.view",
        "View private property details",
        "properties",
        ["ADMIN", "LANDLORD", "TENANT"],
    ),
    ("properties.create", "Create properties", "properties", ["LANDLORD"]),
    ("properties.update", "Edit property and unit details", "properties", ["LANDLORD"]),
    ("properties.manage_owners", "Add and end co-owners", "properties", ["LANDLORD"]),
    ("properties.publish", "Change listing status", "properties", ["LANDLORD"]),
    ("tenancies.view", "View tenancies", "tenancies", ["ADMIN", "LANDLORD", "TENANT"]),
    ("tenancies.create", "Create tenancies", "tenancies", ["LANDLORD"]),
    ("tenancies.update", "Edit tenancy details", "tenancies", ["LANDLORD"]),
    ("tenancies.manage_parties", "Add and remove tenants", "tenancies", ["LANDLORD"]),
    ("files.upload", "Upload files", "files", ["LANDLORD", "TENANT"]),
    ("files.download", "Download files", "files", ["ADMIN", "LANDLORD", "TENANT"]),
    ("conditions.view", "View condition records", "conditions", ["ADMIN", "LANDLORD", "TENANT"]),
    ("conditions.submit_baseline", "Submit baseline condition", "conditions", ["LANDLORD"]),
    (
        "conditions.submit_update",
        "Submit later condition evidence",
        "conditions",
        ["LANDLORD", "TENANT"],
    ),
    ("reviews.view", "View review cases", "reviews", ["ADMIN", "LANDLORD", "TENANT"]),
    ("reviews.submit", "Submit change and correction requests", "reviews", ["LANDLORD", "TENANT"]),
    (
        "reviews.decide",
        "Approve, reject or dispute as opposite side",
        "reviews",
        ["LANDLORD", "TENANT"],
    ),
    ("reviews.escalate", "Escalate a dispute to Admin", "reviews", ["LANDLORD", "TENANT"]),
    ("reviews.request_removal", "Request data removal", "reviews", ["LANDLORD", "TENANT"]),
    ("reviews.admin_review", "Decide Admin-routed cases", "reviews", ["ADMIN"]),
    ("reviews.review_removal", "Decide data removal requests", "reviews", ["ADMIN"]),
    ("maintenance.view", "View maintenance issues", "maintenance", ["ADMIN", "LANDLORD", "TENANT"]),
    ("maintenance.report", "Report an issue", "maintenance", ["LANDLORD", "TENANT"]),
    ("maintenance.confirm_start", "Confirm work started", "maintenance", ["LANDLORD", "TENANT"]),
    (
        "maintenance.propose_closure",
        "Propose closing an issue",
        "maintenance",
        ["LANDLORD", "TENANT"],
    ),
    (
        "maintenance.review_closure",
        "Approve or reject a closure",
        "maintenance",
        ["LANDLORD", "TENANT"],
    ),
    (
        "maintenance.close_vacant",
        "Close directly with no current tenant",
        "maintenance",
        ["LANDLORD"],
    ),
    (
        "maintenance.record_assignment",
        "Record provider engagement",
        "maintenance",
        ["LANDLORD", "TENANT"],
    ),
    ("documents.view", "View documents", "documents", ["ADMIN", "LANDLORD", "TENANT"]),
    ("documents.publish", "Upload document versions", "documents", ["LANDLORD"]),
    ("documents.confirm", "Confirm or flag a document", "documents", ["TENANT"]),
    ("providers.view", "View service providers", "providers", ["ADMIN", "LANDLORD", "TENANT"]),
    ("providers.manage", "Manage providers and recommendations", "providers", ["LANDLORD"]),
    ("providers.manage_categories", "Manage service categories", "providers", ["ADMIN"]),
    (
        "communications.view",
        "View communication logs",
        "communications",
        ["ADMIN", "LANDLORD", "TENANT"],
    ),
    (
        "communications.log",
        "Log an external communication",
        "communications",
        ["LANDLORD", "TENANT"],
    ),
]


def seed(apps, _schema_editor):
    Role = apps.get_model("accounts", "Role")
    Permission = apps.get_model("accounts", "Permission")
    RolePermissionBridge = apps.get_model("accounts", "RolePermissionBridge")
    roles = {role.code: role for role in Role.objects.all()}
    for code, name, module, role_codes in PERMISSIONS:
        permission, _ = Permission.objects.update_or_create(
            code=code, defaults={"name": name, "module": module}
        )
        for role_code in role_codes:
            RolePermissionBridge.objects.get_or_create(role=roles[role_code], permission=permission)


def unseed(apps, _schema_editor):
    codes = [code for code, _, _, _ in PERMISSIONS]
    apps.get_model("accounts", "RolePermissionBridge").objects.filter(
        permission__code__in=codes
    ).delete()
    apps.get_model("accounts", "Permission").objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_seed_roles_and_access_policy")]

    operations = [migrations.RunPython(seed, unseed)]
