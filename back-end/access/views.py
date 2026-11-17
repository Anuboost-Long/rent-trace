from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from access import dtos, resources, services
from accounts.security.mfa_permission import MfaCompleted
from accounts.security.permission_required import HasRequiredPermission
from common.pagination import PagePagination

MANAGE = "access.manage"


class AccessView(APIView):
    permission_classes = [IsAuthenticated, MfaCompleted, HasRequiredPermission]
    required_permissions: dict[str, str] = {}


def _validated(dto_class, data):
    serializer = dto_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class PermissionsView(AccessView):
    """List and create share one path, so they share one class."""

    required_permissions = {"GET": MANAGE, "POST": MANAGE}

    @extend_schema(
        operation_id="access_permissions_list", responses=resources.PermissionResource(many=True)
    )
    def get(self, request):
        return Response(resources.PermissionResource(services.list_permissions(), many=True).data)

    @extend_schema(
        operation_id="access_permissions_create",
        request=dtos.CreatePermissionDto,
        responses={201: resources.PermissionResource},
    )
    def post(self, request):
        data = _validated(dtos.CreatePermissionDto, request.data)
        permission = services.create_permission(
            actor=request.user,
            code=data["code"],
            name=data["name"],
            is_admin_only=data["is_admin_only"],
        )
        return Response(resources.PermissionResource(permission).data, status=201)


class PermissionDetailView(AccessView):
    required_permissions = {"PATCH": MANAGE}

    @extend_schema(
        operation_id="access_permissions_update",
        request=dtos.UpdatePermissionDto,
        responses=resources.PermissionResource,
    )
    def patch(self, request, permission_code):
        data = _validated(dtos.UpdatePermissionDto, request.data)
        permission = services.update_permission(
            actor=request.user,
            code=permission_code,
            changes=services.PermissionChanges(
                name=data.get("name", services.UNSET),
                is_admin_only=data.get("is_admin_only", services.UNSET),
                is_active=data.get("is_active", services.UNSET),
            ),
        )
        return Response(resources.PermissionResource(permission).data)


class PermissionHoldersView(AccessView):
    required_permissions = {"GET": MANAGE}

    @extend_schema(
        operation_id="access_permission_holders", responses=resources.PermissionHoldersResource
    )
    def get(self, request, permission_code):
        data = services.get_permission_holders(code=permission_code)
        return Response(resources.PermissionHoldersResource(data).data)


class GrantsListView(AccessView):
    required_permissions = {"GET": MANAGE}

    @extend_schema(
        operation_id="access_grants_list",
        parameters=[dtos.GrantListQueryDto],
        responses=resources.GrantPageResource,
    )
    def get(self, request):
        query = _validated(dtos.GrantListQueryDto, request.query_params)
        grants = services.list_grants(q=query.get("q"), permission_code=query.get("permission"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(grants, request, view=self)
        return paginator.get_paginated_response(
            resources.grant_list.GrantListItemResource(page, many=True).data
        )


class RolesView(AccessView):
    """List and create share one path, so they share one class."""

    required_permissions = {"GET": MANAGE, "POST": MANAGE}

    @extend_schema(operation_id="access_roles_list", responses=resources.RoleResource(many=True))
    def get(self, request):
        return Response(resources.RoleResource(services.list_roles(), many=True).data)

    @extend_schema(
        operation_id="access_roles_create",
        request=dtos.CreateRoleDto,
        responses={201: resources.RoleResource},
    )
    def post(self, request):
        data = _validated(dtos.CreateRoleDto, request.data)
        role = services.create_role(
            actor=request.user,
            name=data["name"],
            description=data.get("description"),
            parent_code=data.get("parent"),
            permission_codes=data["permissions"],
            reason=data.get("reason"),
        )
        return Response(resources.RoleResource(role).data, status=201)


class RoleDetailView(AccessView):
    required_permissions = {"PATCH": MANAGE}

    @extend_schema(
        operation_id="access_roles_update",
        request=dtos.UpdateRoleDto,
        responses=resources.RoleResource,
    )
    def patch(self, request, role_code):
        data = _validated(dtos.UpdateRoleDto, request.data)
        role = services.update_role(
            actor=request.user,
            role_code=role_code,
            changes=services.RoleChanges(
                name=data.get("name", services.UNSET),
                description=data.get("description", services.UNSET),
                parent_code=data.get("parent", services.UNSET),
                permission_codes=data.get("permissions", services.UNSET),
                is_active=data.get("is_active", services.UNSET),
            ),
            reason=data.get("reason"),
        )
        return Response(resources.RoleResource(role).data)


class UserPermissionsView(AccessView):
    required_permissions = {"GET": MANAGE}

    @extend_schema(
        operation_id="access_user_permissions", responses=resources.UserPermissionsResource
    )
    def get(self, request, user_id):
        data = services.get_user_permissions(user_id=user_id)
        return Response(resources.UserPermissionsResource(data).data)


class UserGrantsView(AccessView):
    required_permissions = {"POST": MANAGE}

    @extend_schema(
        operation_id="access_grants_create",
        request=dtos.GrantPermissionDto,
        responses=resources.UserPermissionsResource,
    )
    def post(self, request, user_id):
        data = _validated(dtos.GrantPermissionDto, request.data)
        services.grant_permission(
            actor=request.user,
            user_id=user_id,
            permission_code=data["permission"],
            reason=data["reason"],
        )
        result = services.get_user_permissions(user_id=user_id)
        return Response(resources.UserPermissionsResource(result).data, status=201)


class UserGrantDetailView(AccessView):
    required_permissions = {"DELETE": MANAGE}

    @extend_schema(
        operation_id="access_grants_revoke",
        request=dtos.RevokePermissionDto,
        responses={204: None},
    )
    def delete(self, request, user_id, permission_code):
        data = _validated(dtos.RevokePermissionDto, request.data)
        services.revoke_permission(
            actor=request.user,
            user_id=user_id,
            permission_code=permission_code,
            reason=data.get("reason"),
        )
        return Response(status=204)


class RoleMembersView(AccessView):
    """List and add share one path, so they share one class."""

    required_permissions = {"GET": MANAGE, "POST": MANAGE}

    @extend_schema(
        operation_id="access_role_members_list",
        parameters=[dtos.GrantListQueryDto],
        responses=resources.RoleMemberPageResource,
    )
    def get(self, request, role_code):
        _, members = services.list_role_members(role_code=role_code)
        paginator = PagePagination()
        page = paginator.paginate_queryset(members, request, view=self)
        return paginator.get_paginated_response(
            resources.role_member.RoleMemberResource(page, many=True).data
        )

    @extend_schema(
        operation_id="access_role_members_add",
        request=dtos.AddRoleMemberDto,
        responses={204: None},
    )
    def post(self, request, role_code):
        data = _validated(dtos.AddRoleMemberDto, request.data)
        services.add_role_member(actor=request.user, role_code=role_code, user_id=data["user_id"])
        return Response(status=204)


class RoleMemberDetailView(AccessView):
    required_permissions = {"DELETE": MANAGE}

    @extend_schema(operation_id="access_role_members_remove", responses={204: None})
    def delete(self, request, role_code, user_id):
        services.remove_role_member(actor=request.user, role_code=role_code, user_id=user_id)
        return Response(status=204)
