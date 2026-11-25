from django.urls import path

from reviews import tenant_views as views

urlpatterns = [
    path("", views.MyEvidenceView.as_view(), name="tenant-condition-evidence"),
    path(
        "<int:request_id>/cancel/",
        views.CancelEvidenceView.as_view(),
        name="tenant-condition-evidence-cancel",
    ),
]
