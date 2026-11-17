from rest_framework.exceptions import PermissionDenied, ValidationError

from accounts.models import Permission
from accounts.services.shared.account_rules import is_admin_side
from accounts.services.shared.privileges import ensure_holds

HIDDEN_RECORDS = "access.view_hidden_records"
ADMIN_MODULES = {"accounts", "access"}
SELF_SERVICE_CODES = {"accounts.update_profile"}


def find_active_permission(code):
    permission = Permission.objects.active().with_code(code).first()
    if permission is None:
        raise ValidationError({"permission": f"No active permission '{code}'."})
    return permission


def ensure_may_change_grant(actor, target, permission):
    if actor.pk == target.pk:
        raise PermissionDenied("You can't change your own permissions.")
    if permission.code == HIDDEN_RECORDS and not actor.is_top_level_admin:
        raise PermissionDenied("Only the super admin can grant or revoke this permission.")
    ensure_holds(actor, [permission.code])


def ensure_may_receive(target, permission):
    if permission.is_admin_only and not is_admin_side(target):
        raise ValidationError({"permission": "Only admins can hold this permission."})
