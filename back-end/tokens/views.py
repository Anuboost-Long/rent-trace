from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from tokens import dtos, resources, services


def _validated(dto_class, data):
    serializer = dto_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class TokensView(PermissionedView):
    required_permissions = {"GET": "tokens.view"}

    @extend_schema(
        operation_id="tokens_list",
        parameters=[dtos.TokenListQueryDto],
        responses=resources.TokenPageResource,
    )
    def get(self, request):
        query = _validated(dtos.TokenListQueryDto, request.query_params)
        sessions = services.list_tokens(q=query.get("q"), status=query.get("status"))
        paginator = PagePagination()
        page = paginator.paginate_queryset(sessions, request, view=self)
        data = resources.TokenResource(
            page, many=True, context={"current_session": request.auth}
        ).data
        return paginator.get_paginated_response(data)


class RevokeTokenView(PermissionedView):
    required_permissions = {"POST": "tokens.revoke"}

    @extend_schema(
        operation_id="tokens_revoke",
        request=dtos.RevokeTokenDto,
        responses=resources.TokenResource,
    )
    def post(self, request, token_id):
        data = _validated(dtos.RevokeTokenDto, request.data)
        session = services.revoke_token(
            actor=request.user,
            current_session=request.auth,
            token_id=token_id,
            reason=data.get("reason"),
        )
        return Response(
            resources.TokenResource(session, context={"current_session": request.auth}).data
        )
