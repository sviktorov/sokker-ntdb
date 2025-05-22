from django.urls import path
from django.views.decorators.cache import cache_page

from . import views


urlpatterns = [
    path(
        "admin-dashboard",
        views.ArcadesAdminDashboard.as_view(),
        name="admin_dashboard_arcades",
    ),
    path(
        "team/<str:team_id>/",
        views.ArcadeTeamDetails.as_view(),
        name="arcade_team_details",
    ),
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
        "<str:category_slug>/<str:cup_id>/stat-pots/",
        views.CupStatPotsCLTemplate.as_view(),
        name="arcade_cup_stat_pots_cl",
    ),
    path(
        "<str:category_slug>/draw/<str:cup_id>/",
        views.CupDrawTemplate.as_view(),
        name="arcade_cup_draw",
    ),
    path(
        "<str:category_slug>/draw-playoffs/<str:cup_id>/",
        views.CupDrawPlayoffsTemplate.as_view(),
        name="arcade_cup_draw_playoffs",
    ),
    path(
        "fixtures/cl/rounds",
        views.CLFixtures.as_view(),
        name="cl_fixtures",
    ),
    path(
        "do_draw_arcades",
        views.CommandFormPlayerUpdate,
        name="do_draw_arcades",
    ),
    path('cup/<int:cup_id>/round/<int:round_id>/image/', views.cup_round_image, name='cup_round_image'),
    path('cup/<int:cup_id>/group/<int:group_id>/standings/image/', views.cup_group_standings_image, name='cup_group_standings_image'),
    path('cup/<int:cup_id>/stats/<str:stat_type>/', 
         cache_page(60 * 60 * 24)(views.CupStatsTemplate.as_view()), 
         name='cup_stats_template'),
    path('cup/<int:cup_id>/stats-teams/<str:stat_type>/', 
         cache_page(60 * 60 * 24)(views.CupStatsTeamsTemplate.as_view()), 
         name='cup_stats_teams_template'),
]
