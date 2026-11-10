from access.services.shared import role_design
from accounts.models import RoleKind, User


def list_role_members(*, role_code):
    role = role_design.find_role(role_code)
    members = User.objects.not_deleted().with_active_roles().with_any_role([role.pk])
    return role, members.newest_first()


def ensure_admin_role(role):
    from rest_framework.exceptions import ValidationError

    if role.kind != RoleKind.ADMIN:
        raise ValidationError("Change tenant and landlord roles on the person's own page.")
