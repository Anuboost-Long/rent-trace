from django.urls import path

from overview import views

urlpatterns = [
    path("", views.LandlordOverviewView.as_view(), name="landlord-overview"),
]
