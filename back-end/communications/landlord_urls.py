from django.urls import path

from communications import landlord_views as views

urlpatterns = [
    path("", views.LandlordContactRequestsView.as_view(), name="landlord-contact-requests"),
    path(
        "<int:request_id>/",
        views.LandlordContactRequestDetailView.as_view(),
        name="landlord-contact-request",
    ),
    path(
        "<int:request_id>/accept/",
        views.AcceptContactRequestView.as_view(),
        name="landlord-contact-request-accept",
    ),
    path(
        "<int:request_id>/decline/",
        views.DeclineContactRequestView.as_view(),
        name="landlord-contact-request-decline",
    ),
    path(
        "<int:request_id>/revoke/",
        views.RevokeContactRequestView.as_view(),
        name="landlord-contact-request-revoke",
    ),
]
