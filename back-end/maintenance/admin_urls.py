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
    path(
        "<int:issue_id>/closure/",
        views.AdminProposeClosureView.as_view(),
        name="admin-maintenance-propose-closure",
    ),
    path(
        "<int:issue_id>/closure/withdraw/",
        views.AdminWithdrawClosureView.as_view(),
        name="admin-maintenance-withdraw-closure",
    ),
    path(
        "<int:issue_id>/closure/<int:proposal_id>/approve/",
        views.AdminApproveClosureView.as_view(),
        name="admin-maintenance-approve-closure",
    ),
    path(
        "<int:issue_id>/closure/<int:proposal_id>/reject/",
        views.AdminRejectClosureView.as_view(),
        name="admin-maintenance-reject-closure",
    ),
    path(
        "<int:issue_id>/assignment/",
        views.AdminAssignProviderView.as_view(),
        name="admin-maintenance-assign-provider",
    ),
    path(
        "<int:issue_id>/assignment/complete/",
        views.AdminCompleteVisitView.as_view(),
        name="admin-maintenance-complete-visit",
    ),
]
