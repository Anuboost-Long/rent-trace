from django.urls import path

from documents import file_views, views

urlpatterns = [
    path("", views.AdminDocumentsView.as_view(), name="admin-documents"),
    path("<int:document_id>/", views.AdminDocumentView.as_view(), name="admin-document"),
    path("cases/", views.AdminDocumentCasesView.as_view(), name="admin-document-cases"),
    path(
        "cases/<int:case_id>/approve/",
        views.DecideDocumentCaseView.as_view(),
        name="admin-document-case-approve",
    ),
    path(
        "cases/<int:case_id>/reject/",
        views.RejectDocumentCaseView.as_view(),
        name="admin-document-case-reject",
    ),
    path(
        "files/<int:file_id>/",
        file_views.AdminDocumentFileView.as_view(),
        name="admin-document-file",
    ),
]
