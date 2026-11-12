from django.urls import path

from maintenance import views

urlpatterns = [
    path("", views.IssuesView.as_view(), name="maintenance"),
    path("<int:issue_id>/", views.IssueDetailView.as_view(), name="maintenance-detail"),
    path(
        "<int:issue_id>/acknowledge/",
        views.AcknowledgeIssueView.as_view(),
        name="maintenance-acknowledge",
    ),
    path("<int:issue_id>/start/", views.StartWorkView.as_view(), name="maintenance-start"),
    path("<int:issue_id>/close/", views.CloseVacantView.as_view(), name="maintenance-close-vacant"),
    path(
        "<int:issue_id>/closure/",
        views.ProposeClosureView.as_view(),
        name="maintenance-propose-closure",
    ),
    path(
        "<int:issue_id>/closure/withdraw/",
        views.WithdrawClosureView.as_view(),
        name="maintenance-withdraw-closure",
    ),
    path(
        "<int:issue_id>/closure/<int:proposal_id>/approve/",
        views.ApproveClosureView.as_view(),
        name="maintenance-approve-closure",
    ),
    path(
        "<int:issue_id>/closure/<int:proposal_id>/reject/",
        views.RejectClosureView.as_view(),
        name="maintenance-reject-closure",
    ),
]
