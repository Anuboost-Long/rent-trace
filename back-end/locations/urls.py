from django.urls import path

from locations import views

urlpatterns = [
    path("states/", views.StatesView.as_view(), name="location-states"),
    path("suburbs/", views.SuburbsView.as_view(), name="location-suburbs"),
]
