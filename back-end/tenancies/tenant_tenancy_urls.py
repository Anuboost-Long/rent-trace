from django.urls import path

from tenancies import tenant_views as views

urlpatterns = [
    path("", views.MyTenanciesView.as_view(), name="tenant-tenancies"),
    path("<int:tenancy_id>/", views.MyTenancyDetailView.as_view(), name="tenant-tenancy"),
    path(
        "<int:tenancy_id>/invitations/",
        views.RequestHousemateView.as_view(),
        name="tenant-tenancy-request-housemate",
    ),
    path(
        "<int:tenancy_id>/invitations/<int:invitation_id>/withdraw/",
        views.WithdrawHousemateView.as_view(),
        name="tenant-tenancy-withdraw-housemate",
    ),
]
