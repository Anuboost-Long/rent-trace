from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from bans import dtos, resources, services
from common.pagination import PagePagination


def _validated(dto_class, data):
    serializer = dto_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class BansView(PermissionedView):
    required_permissions = {"GET": "bans.view"}

    @extend_schema(
        operation_id="bans_list",
        parameters=[dtos.BanListQueryDto],
        responses=resources.BanPageResource,
    )
    def get(self, request):
        query = _validated(dtos.BanListQueryDto, request.query_params)
        bans = services.list_bans(
            q=query.get("q"), status=query.get("status"), ban_type=query.get("type")
        )
        paginator = PagePagination()
        page = paginator.paginate_queryset(bans, request, view=self)
        return paginator.get_paginated_response(resources.BanResource(page, many=True).data)


class LiftBanView(PermissionedView):
    required_permissions = {"POST": "bans.manage"}

    @extend_schema(
        operation_id="bans_lift", request=dtos.LiftBanDto, responses=resources.BanResource
    )
    def post(self, request, ban_id):
        data = _validated(dtos.LiftBanDto, request.data)
        ban = services.lift_ban(actor=request.user, ban_id=ban_id, reason=data["reason"])
        return Response(resources.BanResource(ban).data)
