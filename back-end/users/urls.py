from django.urls import path

from users import views

urlpatterns = [
    path("", views.UsersView.as_view(), name="users"),
    path("all/", views.AllUsersView.as_view(), name="users-all"),
    path("<int:user_id>/", views.UserDetailView.as_view(), name="user-detail"),
    path("<int:user_id>/deactivate/", views.DeactivateUserView.as_view(), name="user-deactivate"),
    path(
        "<int:user_id>/reset-authenticator/",
        views.ResetAuthenticatorView.as_view(),
        name="user-reset-authenticator",
    ),
    path(
        "<int:user_id>/resend-authenticator-notice/",
        views.ResendAuthenticatorNoticeView.as_view(),
        name="user-resend-authenticator-notice",
    ),
    path("<int:user_id>/activate/", views.ActivateUserView.as_view(), name="user-activate"),
]
