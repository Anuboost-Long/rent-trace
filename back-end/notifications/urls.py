from django.urls import path

from notifications import views

urlpatterns = [
    path("", views.NotificationsView.as_view(), name="notifications"),
    path("unread-count/", views.UnreadCountView.as_view(), name="notifications-unread-count"),
    path("read-all/", views.ReadAllNotificationsView.as_view(), name="notifications-read-all"),
    path(
        "<int:notification_id>/read/",
        views.ReadNotificationView.as_view(),
        name="notification-read",
    ),
]
