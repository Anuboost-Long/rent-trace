from django.urls import path

from providers import property_views as views

urlpatterns = [
    path("", views.PropertyProvidersView.as_view(), name="landlord-property-providers"),
    path(
        "<int:provider_id>/",
        views.PropertyProviderLinkView.as_view(),
        name="landlord-property-provider",
    ),
]
