from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.CupIndex.as_view(),
        name="arcade_cup_index",
    ),
    path(
        "<str:category_slug>/medals/",
        views.CupMedals.as_view(),
        name="arcade_cup_medals",
    ),
    path(
        "<str:category_slug>/rank/",
        views.CupRank.as_view(),
        name="arcade_cup_rank",
    ),
    path(
        "<str:category_slug>/<str:cup_id>/",
        views.CupDetails.as_view(),
        name="arcade_cup_details",
    ),
]
