from django.urls import path

from documents import file_views, views

urlpatterns = [
    path("", views.TenantDocumentsView.as_view(), name="tenant-documents"),
    path("<int:document_id>/", views.TenantDocumentView.as_view(), name="tenant-document"),
    path(
        "versions/<int:version_id>/confirm/",
        views.ConfirmVersionView.as_view(),
        name="tenant-document-confirm",
    ),
    path(
        "versions/<int:version_id>/flag/",
        views.FlagVersionView.as_view(),
        name="tenant-document-flag",
    ),
    path(
        "files/<int:file_id>/",
        file_views.TenantDocumentFileView.as_view(),
        name="tenant-document-file",
    ),
]
