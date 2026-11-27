from django.urls import path

from reviews import correction_views as views

urlpatterns = [
    path("", views.LandlordCorrectionsView.as_view(), name="landlord-condition-corrections"),
    path(
        "<int:request_id>/cancel/",
        views.CancelLandlordCorrectionView.as_view(),
        name="landlord-condition-correction-cancel",
    ),
]
