from django.urls import path

from properties import landlord_views as views

urlpatterns = [
    path("", views.LandlordPropertiesView.as_view(), name="landlord-properties"),
    path(
        "<int:property_id>/",
        views.LandlordPropertyDetailView.as_view(),
        name="landlord-property-detail",
    ),
    path(
        "<int:property_id>/units/",
        views.LandlordUnitsView.as_view(),
        name="landlord-property-units",
    ),
    path(
        "<int:property_id>/units/<int:unit_id>/",
        views.LandlordUnitDetailView.as_view(),
        name="landlord-property-unit-detail",
    ),
    path(
        "<int:property_id>/units/<int:unit_id>/occupancy/",
        views.LandlordUnitOccupancyView.as_view(),
        name="landlord-property-unit-occupancy",
    ),
    path(
        "<int:property_id>/files/",
        views.LandlordPropertyFilesView.as_view(),
        name="landlord-property-files",
    ),
    path(
        "<int:property_id>/files/<int:file_id>/",
        views.LandlordPropertyFileDetailView.as_view(),
        name="landlord-property-file-detail",
    ),
    path(
        "<int:property_id>/files/<int:file_id>/content/",
        views.LandlordPropertyFileContentView.as_view(),
        name="landlord-property-file-content",
    ),
    path(
        "<int:property_id>/units/<int:unit_id>/files/",
        views.LandlordPropertyFilesView.as_view(),
        name="landlord-property-unit-files",
    ),
    path(
        "<int:property_id>/units/<int:unit_id>/files/<int:file_id>/",
        views.LandlordPropertyFileDetailView.as_view(),
        name="landlord-property-unit-file-detail",
    ),
    path(
        "<int:property_id>/units/<int:unit_id>/files/<int:file_id>/content/",
        views.LandlordPropertyFileContentView.as_view(),
        name="landlord-property-unit-file-content",
    ),
    path(
        "<int:property_id>/listing/",
        views.LandlordListingStatusView.as_view(),
        name="landlord-property-listing",
    ),
]
