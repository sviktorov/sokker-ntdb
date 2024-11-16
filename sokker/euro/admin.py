from .models import (
    Cup,
    NTTeam,
    CupTeams,
    CupDraw,
    Game,
    RankGroups,
    Winners,
    Medals,
    RankAllTime,
)
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django.contrib import admin


@admin.register(Cup)
class CupAdmin(ImportExportModelAdmin):
    list_display = ("c_name", "c_edition", "c_active", "c_draw_status", "c_status")
    list_filter = ("c_active",)
    ordering = ("c_name",)


@admin.register(NTTeam)
class NTTeamAdmin(ImportExportModelAdmin):
    list_display = ("id", "t_name", "t_sokker_id")
    ordering = ("t_name",)


@admin.register(CupTeams)
class CupTeamsAdmin(ImportExportModelAdmin):
    list_display = ("t_id", "c_id", "g_id")
    ordering = ("c_id",)
    list_filter = ("c_id__c_draw_status", "c_id", "g_id")


@admin.register(CupDraw)
class CupDrawAdmin(ImportExportModelAdmin):
    list_display = ("t_id", "c_id", "g_id")
    ordering = ("c_id",)
    list_filter = ("c_id__c_draw_status", "c_id", "g_id")


@admin.register(Game)
class GameAdmin(ImportExportModelAdmin):
    list_display = (
        "t_id_h",
        "t_id_v",
        "cup_round",
        "goals_home",
        "goals_away",
        "playoff_position",
        "group_id",
    )
    list_filter = (
        "c_id",
        "group_id",
        "cup_round",
        "playoff_position",
    )
    ordering = (
        "t_id_h",
        "t_id_v",
    )


@admin.register(RankGroups)
class RankGroupsAdmin(ImportExportModelAdmin):
    list_display = ("t_id", "c_id", "g_id", "points", "grecieved", "gscored", "gdif")
    list_filter = (
        "c_id",
        "g_id",
    )
    ordering = ("-points", "-gdif")


@admin.register(Medals)
class MedalsAdmin(ImportExportModelAdmin):
    list_display = ("t_id", "position_1", "position_2", "position_3", "position_4")
    list_filter = ("t_id",)
    ordering = ("position_1",)


@admin.register(Winners)
class WinnersAdmin(ImportExportModelAdmin):
    list_display = (
        "team_id",
        "cup_id",
        "position",
    )
    list_filter = (
        "team_id",
        "position",
    )
    ordering = ("cup_id",)


@admin.register(RankAllTime)
class RankAllTimeAdmin(ImportExportModelAdmin):
    list_display = ("t_id", "c_flow", "points", "grecieved", "gscored", "gdif")
    list_filter = (
        "t_id",
        "c_flow",
    )
    ordering = ("-points", "-gdif")
