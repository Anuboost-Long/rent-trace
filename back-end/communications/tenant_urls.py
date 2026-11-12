from django.urls import path

from communications import tenant_views as views

urlpatterns = [
    path("", views.ContactRequestsView.as_view(), name="tenant-contact-requests"),
    path(
        "<int:request_id>/",
        views.ContactRequestDetailView.as_view(),
        name="tenant-contact-request",
    ),
    path(
        "<int:request_id>/cancel/",
        views.CancelContactRequestView.as_view(),
        name="tenant-contact-request-cancel",
    ),
]
