from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from access.services.list_permissions import find_listed_permission
from access.services.shared.rules import ADMIN_MODULES
from accounts.models import Permission


def create_permission(*, actor, code, name, is_admin_only):
    module = code.split(".")[0]
    try:
        _create(code, module, name.strip(), is_admin_only or module in ADMIN_MODULES)
    except IntegrityError as error:
        raise ValidationError({"code": f"The permission '{code}' already exists."}) from error
    return find_listed_permission(code)


@transaction.atomic
def _create(code, module, name, is_admin_only):
    Permission.objects.create(code=code, name=name, module=module, is_admin_only=is_admin_only)
