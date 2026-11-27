from django.urls import path

from reviews import correction_views as views

urlpatterns = [
    path("", views.AdminCorrectionsView.as_view(), name="admin-condition-corrections"),
    path(
        "<int:request_id>/approve/",
        views.ApproveCorrectionView.as_view(),
        name="admin-condition-correction-approve",
    ),
    path(
        "<int:request_id>/reject/",
        views.RejectCorrectionView.as_view(),
        name="admin-condition-correction-reject",
    ),
]
