from django.urls import path

from tenancies import tenant_views as views

urlpatterns = [
    path("", views.MyInvitationsView.as_view(), name="tenant-invitations"),
    path("accept/", views.AcceptByTokenView.as_view(), name="tenant-invitation-accept-token"),
    path(
        "<int:invitation_id>/accept/",
        views.AcceptByIdView.as_view(),
        name="tenant-invitation-accept",
    ),
]
