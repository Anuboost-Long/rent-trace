from django.urls import path

from access import views

urlpatterns = [
    path("permissions/", views.PermissionsView.as_view(), name="access-permissions"),
    path(
        "permissions/<str:permission_code>/",
        views.PermissionDetailView.as_view(),
        name="access-permission-detail",
    ),
    path(
        "permissions/<str:permission_code>/holders/",
        views.PermissionHoldersView.as_view(),
        name="access-permission-holders",
    ),
    path("grants/", views.GrantsListView.as_view(), name="access-grants-list"),
    path("roles/", views.RolesView.as_view(), name="access-roles"),
    path("roles/<str:role_code>/", views.RoleDetailView.as_view(), name="access-role-detail"),
    path(
        "roles/<str:role_code>/members/",
        views.RoleMembersView.as_view(),
        name="access-role-members",
    ),
    path(
        "roles/<str:role_code>/members/<int:user_id>/",
        views.RoleMemberDetailView.as_view(),
        name="access-role-member-detail",
    ),
    path(
        "users/<int:user_id>/permissions/",
        views.UserPermissionsView.as_view(),
        name="access-user-permissions",
    ),
    path("users/<int:user_id>/grants/", views.UserGrantsView.as_view(), name="access-grants"),
    path(
        "users/<int:user_id>/grants/<str:permission_code>/",
        views.UserGrantDetailView.as_view(),
        name="access-grant-detail",
    ),
]
