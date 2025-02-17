from django.urls import path

from . import views


urlpatterns = [
    path(
        "admin-dashboard",
        views.NTDBAdminDashboard.as_view(),
        name="admin_dashboard",
    ),
    path(
        "index",
        views.NTDBIndex.as_view(),
        name="ntdb_index",
    ),
    path(
        "player-update",
        views.PlayerUpdate.as_view(),
        name="player_update",
    ),
    path(
        "player-manual-update",
        views.PlayerManualUpdate.as_view(),
        name="player_manual_update",
    ),

    path(
        "<str:country_name>/best-players",
        views.BestPlayers.as_view(),
        name="best_players",
    ),
    path(
        "<str:country_name>/best-players-all-time",
        views.BestPlayersAll.as_view(),
        name="best_players_all",
    ),
    path(
        "<str:country_name>/best-players-all-time-stats",
        views.BestPlayersAllStats.as_view(),
        name="best_players_all_stats",
    ),
    
    path(
        "<str:country_name>/best-players-team-stats/<str:team_id>",
        views.BestPlayersTeamStats.as_view(),
        name="best_players_team_stats",
    ),
    path(
        "<str:country_name>/best-players-all-time-stats-teams",
        views.BestPlayersAllStatsTeams.as_view(),
        name="best_players_all_stats_teams",
    ),
    path(
        "<str:country_name>/player-history/<str:sokker_id>",
        views.PlayerHistory.as_view(),
        name="player_history",
    ),

    path("run-command/", views.RunCommand, name="run_command"),
]
