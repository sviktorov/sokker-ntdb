from django.urls import path

from . import views


urlpatterns = [
    path(
        "<str:cup_id>/",
        views.CupDetails.as_view(),
        name="cup_details",
    ),
]
