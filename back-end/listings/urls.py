from django.urls import path

from listings import views

urlpatterns = [
    path("", views.ListingsView.as_view(), name="listings"),
    path("places/", views.PlacesView.as_view(), name="listing-places"),
    path("<int:listing_id>/", views.ListingDetailView.as_view(), name="listing-detail"),
    path(
        "<int:listing_id>/photos/<int:file_id>/",
        views.ListingPhotoView.as_view(),
        name="listing-photo",
    ),
]
