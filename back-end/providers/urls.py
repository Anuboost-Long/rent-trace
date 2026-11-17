from django.urls import path

from providers import views

urlpatterns = [
    path("", views.ProvidersView.as_view(), name="landlord-providers"),
    path("categories/", views.ServiceCategoriesView.as_view(), name="landlord-provider-categories"),
    path(
        "<int:provider_id>/",
        views.ProviderDetailView.as_view(),
        name="landlord-provider-detail",
    ),
]
