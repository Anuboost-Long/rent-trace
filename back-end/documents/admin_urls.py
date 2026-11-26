from django.urls import path

from documents import file_views, views

urlpatterns = [
    path("", views.AdminDocumentsView.as_view(), name="admin-documents"),
    path("<int:document_id>/", views.AdminDocumentView.as_view(), name="admin-document"),
    path(
        "files/<int:file_id>/",
        file_views.AdminDocumentFileView.as_view(),
        name="admin-document-file",
    ),
]
