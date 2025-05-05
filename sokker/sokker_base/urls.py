from django.urls import path

from . import views

urlpatterns = [
    path(
        "trophies/<str:country_name>/<str:trophy_type>/",
        views.TeamTrophiesView.as_view(),
        name="team_trophies",
    ),
    path(
        "standings/<str:country_name>/<str:season_id>/<str:league_id>/",
        views.StandingsView.as_view(),
        name="standings",
    ),
    path(
        "standings-all/<str:country_name>/<str:league_id>",
        views.StandingsAllView.as_view(),
        name="standings_all",
    ),
]
