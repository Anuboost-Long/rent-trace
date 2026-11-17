from django.urls import path

from overview import views

urlpatterns = [
    path("", views.OverviewView.as_view(), name="overview"),
]
