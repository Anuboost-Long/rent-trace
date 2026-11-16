from django.urls import path

from providers import admin_views as views

urlpatterns = [
    path("", views.AdminProvidersView.as_view(), name="admin-providers"),
    path(
        "categories/",
        views.AdminServiceCategoriesView.as_view(),
        name="admin-provider-categories",
    ),
]
