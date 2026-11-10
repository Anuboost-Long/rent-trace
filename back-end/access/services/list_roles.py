from accounts.models import Role
from accounts.services.shared.roles import role_effective_codes


def list_roles():
    roles = list(
        Role.objects.with_active_permissions()
        .with_holder_counts()
        .select_related("parent")
        .order_by("kind", "code")
    )
    for role in roles:
        role.inherited_codes = role_effective_codes(role.parent) if role.parent else set()
    return roles


def find_listed_role(code):
    return next(role for role in list_roles() if role.code == code)
