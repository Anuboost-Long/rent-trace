from django.urls import path

from reviews import correction_views as views

urlpatterns = [
    path("", views.TenantCorrectionsView.as_view(), name="tenant-condition-corrections"),
    path(
        "<int:request_id>/cancel/",
        views.CancelTenantCorrectionView.as_view(),
        name="tenant-condition-correction-cancel",
    ),
]
