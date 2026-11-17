from django.urls import path

from tokens import views

urlpatterns = [
    path("", views.TokensView.as_view(), name="tokens"),
    path("<int:token_id>/revoke/", views.RevokeTokenView.as_view(), name="token-revoke"),
]
