from django.urls import path

from tenancies import landlord_views as views

urlpatterns = [
    path("", views.LandlordTenanciesView.as_view(), name="landlord-tenancies"),
    path("<int:tenancy_id>/", views.LandlordTenancyDetailView.as_view(), name="landlord-tenancy"),
    path(
        "<int:tenancy_id>/invitations/",
        views.LandlordInvitationsView.as_view(),
        name="landlord-tenancy-invitations",
    ),
    path(
        "<int:tenancy_id>/invitations/<int:invitation_id>/resend/",
        views.LandlordResendInvitationView.as_view(),
        name="landlord-tenancy-invitation-resend",
    ),
    path(
        "<int:tenancy_id>/invitations/<int:invitation_id>/revoke/",
        views.LandlordRevokeInvitationView.as_view(),
        name="landlord-tenancy-invitation-revoke",
    ),
]
