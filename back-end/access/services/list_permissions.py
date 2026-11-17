from rest_framework.exceptions import NotFound

from accounts.models import Permission


def list_permissions():
    return list(Permission.objects.with_active_roles().order_by("module", "code"))


def find_listed_permission(code):
    permission = Permission.objects.with_active_roles().with_code(code).first()
    if permission is None:
        raise NotFound("No permission with this code.")
    return permission
