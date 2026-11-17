from django.urls import path

from providers import tenant_views as views

urlpatterns = [
    path("", views.MyPropertyProvidersView.as_view(), name="tenant-tenancy-providers"),
]
