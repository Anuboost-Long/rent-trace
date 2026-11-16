from django.urls import path

from maintenance import admin_views as views

urlpatterns = [
    path("", views.AdminIssuesView.as_view(), name="admin-maintenance"),
    path("<int:issue_id>/", views.AdminIssueDetailView.as_view(), name="admin-maintenance-detail"),
]
