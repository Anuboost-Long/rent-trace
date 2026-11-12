from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.security.permissioned_view import PermissionedView
from common.pagination import PagePagination
from tenancies import dtos, resources, services


def validated(dto_class, data):
    serializer = dto_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class TenancyScope:
    """Admins see every tenancy; the landlord views narrow this to the properties they own."""

    def owned_by(self, request):
        return None


def detail(tenancy_id, owned_by):
    return resources.TenancyDetailResource(
        services.get_tenancy(tenancy_id=tenancy_id, owned_by=owned_by)
    ).data


class TenanciesView(TenancyScope, PermissionedView):
    required_permissions = {
        "GET": "tenancies.admin_view",
        "POST": "tenancies.admin_manage",
    }

    @extend_schema(
        operation_id="tenancies_list",
        parameters=[dtos.TenancyListQueryDto],
        responses=resources.TenancyPageResource,
    )
    def get(self, request):
        query = validated(dtos.TenancyListQueryDto, request.query_params)
        tenancies = services.list_tenancies(
            q=query.get("q"), status=query.get("status"), owned_by=self.owned_by(request)
        )
        paginator = PagePagination()
        page = paginator.paginate_queryset(tenancies, request, view=self)
        return paginator.get_paginated_response(
            resources.TenancySummaryResource(page, many=True).data
        )

    @extend_schema(
        request=dtos.CreateTenancyDto,
        responses={201: resources.TenancyDetailResource},
    )
    def post(self, request):
        fields = validated(dtos.CreateTenancyDto, request.data)
        created = services.create_tenancy(
            actor=request.user, fields=fields, owned_by=self.owned_by(request)
        )
        return Response(detail(created.pk, self.owned_by(request)), status=201)


class TenancyDetailView(TenancyScope, PermissionedView):
    required_permissions = {"GET": "tenancies.admin_view"}

    @extend_schema(responses=resources.TenancyDetailResource)
    def get(self, request, tenancy_id):
        return Response(detail(tenancy_id, self.owned_by(request)))


class InvitationsView(TenancyScope, PermissionedView):
    required_permissions = {"POST": "tenancies.admin_manage"}

    @extend_schema(
        request=dtos.InviteTenantDto,
        responses={201: resources.InvitationResource},
    )
    def post(self, request, tenancy_id):
        fields = validated(dtos.InviteTenantDto, request.data)
        invitation = services.invite_tenant(
            actor=request.user,
            tenancy_id=tenancy_id,
            fields=fields,
            owned_by=self.owned_by(request),
        )
        return Response(resources.InvitationResource(invitation).data, status=201)


class ResendInvitationView(TenancyScope, PermissionedView):
    required_permissions = {"POST": "tenancies.admin_manage"}

    @extend_schema(
        request=None,
        responses=resources.InvitationResource,
    )
    def post(self, request, tenancy_id, invitation_id):
        invitation = services.resend_invitation(
            actor=request.user,
            tenancy_id=tenancy_id,
            invitation_id=invitation_id,
            owned_by=self.owned_by(request),
        )
        return Response(resources.InvitationResource(invitation).data)


class RevokeInvitationView(TenancyScope, PermissionedView):
    required_permissions = {"POST": "tenancies.admin_manage"}

    @extend_schema(
        request=None,
        responses=resources.InvitationResource,
    )
    def post(self, request, tenancy_id, invitation_id):
        invitation = services.revoke_invitation(
            actor=request.user,
            tenancy_id=tenancy_id,
            invitation_id=invitation_id,
            owned_by=self.owned_by(request),
        )
        return Response(resources.InvitationResource(invitation).data)
