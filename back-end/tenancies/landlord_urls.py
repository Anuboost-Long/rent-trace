from django.urls import path

from tenancies import landlord_views as views

urlpatterns = [
    path("", views.LandlordTenanciesView.as_view(), name="landlord-tenancies"),
    path("<int:tenancy_id>/", views.LandlordTenancyDetailView.as_view(), name="landlord-tenancy"),
    path(
        "<int:tenancy_id>/changes/<int:change_id>/withdraw/",
        views.LandlordWithdrawTermChangeView.as_view(),
        name="landlord-tenancy-terms-withdraw",
    ),
    path(
        "<int:tenancy_id>/activate/",
        views.LandlordActivateTenancyView.as_view(),
        name="landlord-tenancy-activate",
    ),
    path(
        "<int:tenancy_id>/end/",
        views.LandlordEndTenancyView.as_view(),
        name="landlord-tenancy-end",
    ),
    path(
        "<int:tenancy_id>/cancel/",
        views.LandlordCancelTenancyView.as_view(),
        name="landlord-tenancy-cancel",
    ),
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
    path(
        "<int:tenancy_id>/invitations/<int:invitation_id>/approve/",
        views.LandlordApproveHousemateView.as_view(),
        name="landlord-tenancy-invitation-approve",
    ),
    path(
        "<int:tenancy_id>/invitations/<int:invitation_id>/decline/",
        views.LandlordDeclineHousemateView.as_view(),
        name="landlord-tenancy-invitation-decline",
    ),
]
