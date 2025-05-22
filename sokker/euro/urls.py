from django.urls import path
from django.views.decorators.cache import cache_page
from . import views


urlpatterns = [
    path(
        "admin-dashboard",
        views.EuroAdminDashboard.as_view(),
        name="admin_dashboard_euro",
    ),
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
    path('cup/<int:cup_id>/group/<int:group_id>/round/<int:round_id>/image/', views.cup_round_image, name='cup_round_image_euro'),
    path('cup/<int:cup_id>/group/<int:group_id>/standings/image/', views.cup_group_standings_image, name='cup_group_standings_image_euro'),
    path('cup/<int:cup_id>/stats/<str:stat_type>/', 
         cache_page(60 * 60 * 24)(views.EuroCupStatsTemplate.as_view()), 
         name='euro_cup_stats_template'),

]
