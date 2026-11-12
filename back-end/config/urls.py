"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("api/auth/", include("accounts.urls")),
    path("api/users/", include("users.urls")),
    path("api/access/", include("access.urls")),
    path("api/bans/", include("bans.urls")),
    path("api/overview/", include("overview.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/maintenance/", include("maintenance.urls")),
    path("api/tokens/", include("tokens.urls")),
    path("api/locations/", include("locations.urls")),
    path("api/public/listings/", include("listings.urls")),
    path("api/properties/", include("properties.urls")),
    path("api/landlord/properties/", include("properties.landlord_urls")),
    path("api/tenancies/", include("tenancies.urls")),
    path("api/landlord/tenancies/", include("tenancies.landlord_urls")),
    path("api/tenant/invitations/", include("tenancies.tenant_urls")),
    path("api/tenant/tenancies/", include("tenancies.tenant_tenancy_urls")),
    path("api/tenant/contact-requests/", include("communications.tenant_urls")),
    path("api/landlord/contact-requests/", include("communications.landlord_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
