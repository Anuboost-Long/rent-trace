from django.urls import path

from reviews import file_views
from reviews import tenant_views as views

urlpatterns = [
    path("", views.MyEvidenceView.as_view(), name="tenant-condition-evidence"),
    path(
        "<int:request_id>/photos/",
        file_views.AddEvidencePhotoView.as_view(),
        name="tenant-condition-evidence-add-photo",
    ),
    path(
        "photos/<int:file_id>/",
        file_views.TenantEvidencePhotoView.as_view(),
        name="tenant-condition-evidence-photo",
    ),
    path(
        "<int:request_id>/escalate/",
        views.EscalateMyEvidenceView.as_view(),
        name="tenant-condition-evidence-escalate",
    ),
    path(
        "<int:request_id>/cancel/",
        views.CancelEvidenceView.as_view(),
        name="tenant-condition-evidence-cancel",
    ),
]
