from django.urls import path

from conditions import views

urlpatterns = [
    path("", views.ConditionsView.as_view(), name="landlord-conditions"),
    path("<int:condition_id>/", views.ConditionDetailView.as_view(), name="landlord-condition"),
]
