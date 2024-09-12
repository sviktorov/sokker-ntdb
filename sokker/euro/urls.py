from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.CupIndex.as_view(),
        name="cup_index",
    ),
    path(
        "<str:cup_id>/",
        views.CupDetails.as_view(),
        name="cup_details",
    ),
]
