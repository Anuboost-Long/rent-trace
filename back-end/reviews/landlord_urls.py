from django.urls import path

from reviews import file_views
from reviews import landlord_views as views

urlpatterns = [
    path("", views.UnitEvidenceView.as_view(), name="landlord-condition-evidence"),
    path(
        "<int:request_id>/approve/",
        views.ApproveEvidenceView.as_view(),
        name="landlord-condition-evidence-approve",
    ),
    path(
        "photos/<int:file_id>/",
        file_views.LandlordEvidencePhotoView.as_view(),
        name="landlord-condition-evidence-photo",
    ),
    path(
        "<int:request_id>/escalate/",
        views.EscalateEvidenceView.as_view(),
        name="landlord-condition-evidence-escalate",
    ),
    path(
        "<int:request_id>/reject/",
        views.RejectEvidenceView.as_view(),
        name="landlord-condition-evidence-reject",
    ),
]
