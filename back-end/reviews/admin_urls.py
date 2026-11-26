from django.urls import path

from reviews import admin_views as views
from reviews import file_views

urlpatterns = [
    path(
        "photos/<int:file_id>/",
        file_views.AdminEvidencePhotoView.as_view(),
        name="admin-review-photo",
    ),
    path("", views.ReviewCasesView.as_view(), name="admin-review-cases"),
    path(
        "<int:case_id>/approve/", views.ApproveCaseView.as_view(), name="admin-review-case-approve"
    ),
    path("<int:case_id>/reject/", views.RejectCaseView.as_view(), name="admin-review-case-reject"),
]
