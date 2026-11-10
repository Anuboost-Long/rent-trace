from django.urls import path

from bans import views

urlpatterns = [
    path("", views.BansView.as_view(), name="bans"),
    path("<int:ban_id>/lift/", views.LiftBanView.as_view(), name="ban-lift"),
]
