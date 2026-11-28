from django.urls import path

from reviews import removal_views as views

urlpatterns = [
    path("", views.AdminRemovalsView.as_view(), name="admin-removal-requests"),
    path("<int:request_id>/", views.AdminRemovalView.as_view(), name="admin-removal-request"),
    path(
        "<int:request_id>/approve/",
        views.ApproveRemovalView.as_view(),
        name="admin-removal-request-approve",
    ),
    path(
        "<int:request_id>/reject/",
        views.RejectRemovalView.as_view(),
        name="admin-removal-request-reject",
    ),
]
