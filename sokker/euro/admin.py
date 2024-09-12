from .models import Cup, NTTeam, CupTeams, CupDraw, Game, RankGroups
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django.contrib import admin


@admin.register(Cup)
class CupAdmin(ImportExportModelAdmin):
    list_display = ("c_name", "c_edition", "c_active")
    list_filter = ("c_active",)
    ordering = ("c_name",)


@admin.register(NTTeam)
class NTTeamAdmin(ImportExportModelAdmin):
    list_display = ("t_name",)
    ordering = ("t_name",)


@admin.register(CupTeams)
class CupTeamsAdmin(ImportExportModelAdmin):
    list_display = ("t_id", "c_id", "g_id")
    ordering = ("c_id",)


@admin.register(CupDraw)
class CupDrawAdmin(ImportExportModelAdmin):
    list_display = ("t_id", "c_id", "g_id")
    ordering = ("c_id",)


@admin.register(Game)
class GameAdmin(ImportExportModelAdmin):
    list_display = (
        "t_id_h",
        "t_id_v",
        "goals_home",
        "goals_away",
        "playoff_position",
    )
    list_filter = (
        "c_id",
        "playoff_position",
    )
    ordering = (
        "t_id_h",
        "t_id_v",
    )


@admin.register(RankGroups)
class RankGroupsAdmin(ImportExportModelAdmin):
    list_display = ("t_id", "c_id", "points", "grecieved", "gscored", "gdif")
    list_filter = (
        "c_id",
        "g_id",
    )
    ordering = ("-points", "-gdif")
