from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.security.mfa_permission import MfaCompleted
from accounts.security.permission_required import HasRequiredPermission
from accounts.security.super_admin_permission import IsSuperAdmin
from common.pagination import PagePagination
from users import dtos, resources, services


def _filter_from(request, dto_class):
    serializer = dto_class(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    return services.UserFilter(q=data.get("q"), role=data.get("role"), status=data.get("status"))


class AdminView(APIView):
    permission_classes = [IsAuthenticated, MfaCompleted, HasRequiredPermission]
    required_permissions: dict[str, str] = {}


class UsersView(AdminView):
    required_permissions = {"GET": "accounts.view", "POST": "accounts.create"}

    """List and create share one path, so they share one class; each method calls one service."""

    @extend_schema(
        operation_id="users_list",
        parameters=[dtos.UserListQueryDto],
        responses=resources.UserPageResource,
    )
    def get(self, request):
        users_filter = _filter_from(request, dtos.UserListQueryDto)
        paginator = PagePagination()
        page = paginator.paginate_queryset(
            services.list_users(users_filter=users_filter), request, view=self
        )
        return paginator.get_paginated_response(resources.UserSummaryResource(page, many=True).data)

    @extend_schema(
        operation_id="users_create",
        request=dtos.CreateUserDto,
        responses={201: resources.UserDetailResource},
    )
    def post(self, request):
        serializer = dtos.CreateUserDto(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = services.create_user(
            actor=request.user,
            new_user=services.NewUser(
                email=data["email"],
                password=data["password"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role_codes=data["roles"],
            ),
        )
        return Response(resources.UserDetailResource(user).data, status=201)


class AllUsersView(AdminView):
    required_permissions = {"GET": "accounts.view"}

    @extend_schema(
        parameters=[dtos.UserFilterDto], responses=resources.UserOptionResource(many=True)
    )
    def get(self, request):
        users = services.list_all_users(users_filter=_filter_from(request, dtos.UserFilterDto))
        return Response(resources.UserOptionResource(users, many=True).data)


class UserDetailView(AdminView):
    required_permissions = {
        "GET": "accounts.view",
        "PATCH": "accounts.update",
        "DELETE": "accounts.delete",
    }

    """Read, edit and delete share one path, so they share one class."""

    @extend_schema(responses=resources.UserDetailResource)
    def get(self, request, user_id):
        return Response(resources.UserDetailResource(services.get_user(user_id=user_id)).data)

    @extend_schema(
        operation_id="users_update",
        request=dtos.UpdateUserDto,
        responses=resources.UserDetailResource,
    )
    def patch(self, request, user_id):
        serializer = dtos.UpdateUserDto(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        phone = data.get("phone_number", services.UNSET)
        user = services.update_user(
            actor=request.user,
            user_id=user_id,
            changes=services.UserChanges(
                first_name=data.get("first_name", services.UNSET),
                last_name=data.get("last_name", services.UNSET),
                phone_number=(phone or None) if phone is not services.UNSET else phone,
                role_codes=data.get("roles", services.UNSET),
            ),
        )
        return Response(resources.UserDetailResource(user).data)

    @extend_schema(operation_id="users_delete", request=dtos.UserReasonDto, responses={204: None})
    def delete(self, request, user_id):
        serializer = dtos.UserReasonDto(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.delete_user(
            actor=request.user, user_id=user_id, reason=serializer.validated_data.get("reason")
        )
        return Response(status=204)


class DeactivateUserView(AdminView):
    required_permissions = {"POST": "accounts.manage"}

    @extend_schema(
        operation_id="users_deactivate",
        request=dtos.UserReasonDto,
        responses=resources.UserDetailResource,
    )
    def post(self, request, user_id):
        serializer = dtos.UserReasonDto(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.deactivate_user(
            actor=request.user, user_id=user_id, reason=serializer.validated_data.get("reason")
        )
        return Response(resources.UserDetailResource(user).data)


class ResetAuthenticatorView(AdminView):
    permission_classes = [*AdminView.permission_classes, IsSuperAdmin]
    required_permissions = {"POST": "accounts.manage"}

    @extend_schema(
        operation_id="users_reset_authenticator",
        request=dtos.ResetAuthenticatorDto,
        responses=resources.ResetAuthenticatorResource,
    )
    def post(self, request, user_id):
        serializer = dtos.ResetAuthenticatorDto(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.reset_authenticator(
            actor=request.user, user_id=user_id, reason=serializer.validated_data["reason"]
        )
        return Response(
            {**resources.UserDetailResource(result.user).data, "notice_sent": result.notice_sent}
        )


class ResendAuthenticatorNoticeView(AdminView):
    permission_classes = [*AdminView.permission_classes, IsSuperAdmin]
    required_permissions = {"POST": "accounts.manage"}

    @extend_schema(
        operation_id="users_resend_authenticator_notice",
        request=None,
        responses=resources.NoticeSentResource,
    )
    def post(self, request, user_id):
        sent = services.resend_authenticator_notice(actor=request.user, user_id=user_id)
        return Response({"notice_sent": sent})


class ActivateUserView(AdminView):
    required_permissions = {"POST": "accounts.manage"}

    @extend_schema(
        operation_id="users_activate",
        request=dtos.UserReasonDto,
        responses=resources.UserDetailResource,
    )
    def post(self, request, user_id):
        serializer = dtos.UserReasonDto(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.activate_user(
            actor=request.user, user_id=user_id, reason=serializer.validated_data.get("reason")
        )
        return Response(resources.UserDetailResource(user).data)
