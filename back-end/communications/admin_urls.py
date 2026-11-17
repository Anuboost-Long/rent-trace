from django.urls import path

from communications import admin_views as views

urlpatterns = [
    path("", views.AdminContactRequestsView.as_view(), name="admin-contact-requests"),
    path(
        "<int:request_id>/",
        views.AdminContactRequestDetailView.as_view(),
        name="admin-contact-request",
    ),
]
