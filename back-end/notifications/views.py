from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.security.mfa_permission import MfaCompleted
from common.pagination import PagePagination
from notifications import dtos, resources, services


class InboxView(APIView):
    """Everyone signed in has an inbox; each request only ever touches the caller's own."""

    permission_classes = [IsAuthenticated, MfaCompleted]


class NotificationsView(InboxView):
    @extend_schema(
        operation_id="notifications_list",
        parameters=[dtos.NotificationListQueryDto],
        responses=resources.NotificationPageResource,
    )
    def get(self, request):
        query = dtos.NotificationListQueryDto(data=request.query_params)
        query.is_valid(raise_exception=True)
        inbox = services.list_notifications(
            user=request.user, unread_only=query.validated_data.get("unread", False)
        )
        paginator = PagePagination()
        page = paginator.paginate_queryset(inbox, request, view=self)
        return paginator.get_paginated_response(
            resources.NotificationResource(page, many=True).data
        )


class UnreadCountView(InboxView):
    @extend_schema(responses=resources.UnreadCountResource)
    def get(self, request):
        return Response({"unread": services.count_unread(user=request.user)})


class ReadNotificationView(InboxView):
    @extend_schema(request=None, responses=resources.NotificationResource)
    def post(self, request, notification_id):
        found = services.mark_read(user=request.user, notification_id=notification_id)
        return Response(resources.NotificationResource(found).data)


class ReadAllNotificationsView(InboxView):
    @extend_schema(request=None, responses=resources.MarkedReadResource)
    def post(self, request):
        return Response({"marked": services.mark_all_read(user=request.user)})
