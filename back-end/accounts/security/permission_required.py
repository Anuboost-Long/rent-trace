from django.utils import timezone
from rest_framework.permissions import BasePermission

from accounts.services.shared.permissions import has_permission


class HasRequiredPermission(BasePermission):
    """The view lists one permission code per HTTP method in `required_permissions`."""

    message = "You don't have permission to do this."

    def has_permission(self, request, view):
        code = view.required_permissions.get(request.method)
        return code is not None and has_permission(request.user, code, timezone.now())
