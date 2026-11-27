from django.urls import path

from reviews import admin_evidence_views as views

urlpatterns = [
    path("", views.AdminEvidenceView.as_view(), name="admin-condition-evidence"),
    path(
        "<int:request_id>/approve/",
        views.ApproveForLandlordView.as_view(),
        name="admin-condition-evidence-approve",
    ),
    path(
        "<int:request_id>/reject/",
        views.RejectForLandlordView.as_view(),
        name="admin-condition-evidence-reject",
    ),
    path(
        "<int:request_id>/request-information/",
        views.RequestInformationForLandlordView.as_view(),
        name="admin-condition-evidence-request-information",
    ),
    path(
        "<int:request_id>/cancel/",
        views.CancelForTenantView.as_view(),
        name="admin-condition-evidence-cancel",
    ),
    path(
        "<int:request_id>/respond/",
        views.RespondForTenantView.as_view(),
        name="admin-condition-evidence-respond",
    ),
]
