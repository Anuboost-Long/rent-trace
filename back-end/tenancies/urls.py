from django.urls import path

from tenancies import views

urlpatterns = [
    path("", views.TenanciesView.as_view(), name="tenancies"),
    path("<int:tenancy_id>/", views.TenancyDetailView.as_view(), name="tenancy-detail"),
    path(
        "<int:tenancy_id>/invitations/",
        views.InvitationsView.as_view(),
        name="tenancy-invitations",
    ),
    path(
        "<int:tenancy_id>/invitations/<int:invitation_id>/resend/",
        views.ResendInvitationView.as_view(),
        name="tenancy-invitation-resend",
    ),
    path(
        "<int:tenancy_id>/invitations/<int:invitation_id>/revoke/",
        views.RevokeInvitationView.as_view(),
        name="tenancy-invitation-revoke",
    ),
]
