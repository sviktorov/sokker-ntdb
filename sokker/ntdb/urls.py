from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.NTDBIndex.as_view(),
        name="ntdb_index",
    ),
    path(
        "player-update",
        views.PlayerUpdate.as_view(),
        name="player_update",
    ),
    path(
        "<str:country_name>/best-players",
        views.BestPlayers.as_view(),
        name="best_players",
    ),
    path(
        "<str:country_name>/best-players-all",
        views.debug_view,
        name="best_players_all_debug",
    ),
    path(
        "<str:country_name>/best-players-all-time",
        views.BestPlayersAll.as_view(),
        name="best_players_all",
    ),
    path(
        "<str:country_name>/player-history/<str:sokker_id>",
        views.PlayerHistory.as_view(),
        name="player_history",
    ),
    path(
        "form-player-update/", views.CommandFormPlayerUpdate, name="form_player_update"
    ),
    path("archive-players/", views.CommandArchivePlayers, name="archive_players"),
    path("update-teams/", views.CommandUpdateTeams, name="sokker_update_teams"),
    path(
        "fix-player-position/",
        views.CommandFixPlayerPosition,
        name="fix_player_position",
    ),
]
