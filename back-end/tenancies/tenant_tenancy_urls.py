from django.urls import path

from tenancies import tenant_views as views

urlpatterns = [
    path("", views.MyTenanciesView.as_view(), name="tenant-tenancies"),
    path("<int:tenancy_id>/", views.MyTenancyDetailView.as_view(), name="tenant-tenancy"),
]
