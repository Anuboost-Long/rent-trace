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
    path("api/admin/maintenance/", include("maintenance.admin_urls")),
    path("api/tokens/", include("tokens.urls")),
    path("api/locations/", include("locations.urls")),
    path("api/public/listings/", include("listings.urls")),
    path("api/properties/", include("properties.urls")),
    path("api/landlord/overview/", include("overview.landlord_urls")),
    path("api/landlord/properties/", include("properties.landlord_urls")),
    path("api/tenancies/", include("tenancies.urls")),
    path("api/landlord/tenancies/", include("tenancies.landlord_urls")),
    path("api/tenant/invitations/", include("tenancies.tenant_urls")),
    path("api/tenant/tenancies/", include("tenancies.tenant_tenancy_urls")),
    path("api/tenant/tenancies/<int:tenancy_id>/providers/", include("providers.tenant_urls")),
    path("api/admin/contact-requests/", include("communications.admin_urls")),
    path("api/tenant/contact-requests/", include("communications.tenant_urls")),
    path("api/landlord/contact-requests/", include("communications.landlord_urls")),
    path("api/landlord/conditions/", include("conditions.urls")),
    path("api/landlord/condition-evidence/", include("reviews.landlord_urls")),
    path("api/admin/review-cases/", include("reviews.admin_urls")),
    path("api/admin/documents/", include("documents.admin_urls")),
    path("api/landlord/documents/", include("documents.landlord_urls")),
    path("api/tenant/tenancies/<int:tenancy_id>/documents/", include("documents.tenant_urls")),
    path("api/admin/removal-requests/", include("reviews.admin_removal_urls")),
    path("api/landlord/removal-requests/", include("reviews.landlord_removal_urls")),
    path(
        "api/tenant/tenancies/<int:tenancy_id>/removal-requests/",
        include("reviews.tenant_removal_urls"),
    ),
    path("api/admin/condition-evidence/", include("reviews.admin_evidence_urls")),
    path("api/admin/condition-corrections/", include("reviews.admin_correction_urls")),
    path("api/landlord/condition-corrections/", include("reviews.landlord_correction_urls")),
    path(
        "api/tenant/tenancies/<int:tenancy_id>/condition-corrections/",
        include("reviews.tenant_correction_urls"),
    ),
    path(
        "api/tenant/tenancies/<int:tenancy_id>/condition-evidence/",
        include("reviews.tenant_urls"),
    ),
    path(
        "api/landlord/properties/<int:property_id>/providers/", include("providers.property_urls")
    ),
    path("api/landlord/providers/", include("providers.urls")),
    path("api/admin/providers/", include("providers.admin_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
