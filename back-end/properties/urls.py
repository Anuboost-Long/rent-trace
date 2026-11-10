from django.urls import path

from properties import file_views, views

urlpatterns = [
    path("", views.PropertiesView.as_view(), name="properties"),
    path("owner-options/", views.OwnerOptionsView.as_view(), name="property-owner-options"),
    path("<int:property_id>/", views.PropertyDetailView.as_view(), name="property-detail"),
    path("<int:property_id>/units/", views.UnitsView.as_view(), name="property-units"),
    path(
        "<int:property_id>/units/<int:unit_id>/",
        views.UnitDetailView.as_view(),
        name="property-unit-detail",
    ),
    path("<int:property_id>/files/", file_views.PropertyFilesView.as_view(), name="property-files"),
    path(
        "<int:property_id>/files/<int:file_id>/",
        file_views.PropertyFileDetailView.as_view(),
        name="property-file-detail",
    ),
    path(
        "<int:property_id>/files/<int:file_id>/content/",
        file_views.PropertyFileContentView.as_view(),
        name="property-file-content",
    ),
    path(
        "<int:property_id>/units/<int:unit_id>/files/",
        file_views.PropertyFilesView.as_view(),
        name="property-unit-files",
    ),
    path(
        "<int:property_id>/units/<int:unit_id>/files/<int:file_id>/",
        file_views.PropertyFileDetailView.as_view(),
        name="property-unit-file-detail",
    ),
    path(
        "<int:property_id>/units/<int:unit_id>/files/<int:file_id>/content/",
        file_views.PropertyFileContentView.as_view(),
        name="property-unit-file-content",
    ),
]
