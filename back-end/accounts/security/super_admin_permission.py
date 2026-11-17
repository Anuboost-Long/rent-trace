from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    message = "Only a super admin can do this."

    def has_permission(self, request, view):
        return request.user.is_top_level_admin
