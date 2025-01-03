from django.urls import path

from . import views


urlpatterns = [
    path(
        "cups",
        views.CupIndex.as_view(),
        name="arcade_cup_index",
    ),
    path(
        "<str:category_slug>/",
        views.CupIndexCategory.as_view(),
        name="arcade_cup_index_category",
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
    path(
        "<str:category_slug>/<str:cup_id>/fixtures/<str:group_id>/",
        views.CupFixtures.as_view(),
        name="arcade_cup_fixtures_groups",
    ),
    path(
        "<str:category_slug>/draw/<str:cup_id>/",
        views.CupDrawTemplate.as_view(),
        name="arcade_cup_draw",
    ),
    path(
        "fixtures/cl/rounds",
        views.CLFixtures.as_view(),
        name="cl_fixtures",
    ),
]
