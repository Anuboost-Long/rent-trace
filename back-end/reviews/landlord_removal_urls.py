from django.urls import path

from reviews import removal_views as views

urlpatterns = [
    path("", views.LandlordRemovalsView.as_view(), name="landlord-removal-requests"),
    path(
        "<int:request_id>/cancel/",
        views.CancelLandlordRemovalView.as_view(),
        name="landlord-removal-request-cancel",
    ),
]
