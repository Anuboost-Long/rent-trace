from django.urls import path

from maintenance import admin_views as views

urlpatterns = [
    path("", views.AdminIssuesView.as_view(), name="admin-maintenance"),
    path("<int:issue_id>/", views.AdminIssueDetailView.as_view(), name="admin-maintenance-detail"),
    path(
        "<int:issue_id>/photos/<int:file_id>/",
        views.AdminIssuePhotoView.as_view(),
        name="admin-maintenance-photo",
    ),
    path(
        "<int:issue_id>/acknowledge/",
        views.AdminAcknowledgeIssueView.as_view(),
        name="admin-maintenance-acknowledge",
    ),
    path(
        "<int:issue_id>/start/",
        views.AdminStartWorkView.as_view(),
        name="admin-maintenance-start",
    ),
    path(
        "<int:issue_id>/close/",
        views.AdminCloseVacantView.as_view(),
        name="admin-maintenance-close",
    ),
]
