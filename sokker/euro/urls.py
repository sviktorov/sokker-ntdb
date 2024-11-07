from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.CupIndex.as_view(),
        name="cup_index",
    ),
    path(
        "medals/",
        views.CupMedals.as_view(),
        name="cup_medals",
    ),
    path(
        "rank/",
        views.CupRank.as_view(),
        name="cup_rank",
    ),
    path(
        "<str:cup_id>/",
        views.CupDetails.as_view(),
        name="cup_details",
    ),
    path(
        "<str:cup_id>/draw",
        views.CupDrawTemplate.as_view(),
        name="cup_draw",
    ),
    path(
        "do_draw",
        views.CommandFormPlayerUpdate,
        name="do_draw",
    ),
]
