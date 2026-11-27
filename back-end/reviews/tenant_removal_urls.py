from django.urls import path

from reviews import removal_views as views

urlpatterns = [
    path("", views.TenantRemovalsView.as_view(), name="tenant-removal-requests"),
    path(
        "<int:request_id>/cancel/",
        views.CancelTenantRemovalView.as_view(),
        name="tenant-removal-request-cancel",
    ),
]
