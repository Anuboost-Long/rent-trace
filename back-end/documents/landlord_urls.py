from django.urls import path

from documents import file_views, views

urlpatterns = [
    path("", views.LandlordDocumentsView.as_view(), name="landlord-documents"),
    path("<int:document_id>/", views.LandlordDocumentView.as_view(), name="landlord-document"),
    path(
        "<int:document_id>/versions/",
        views.LandlordDocumentVersionsView.as_view(),
        name="landlord-document-versions",
    ),
    path(
        "files/<int:file_id>/",
        file_views.LandlordDocumentFileView.as_view(),
        name="landlord-document-file",
    ),
]
