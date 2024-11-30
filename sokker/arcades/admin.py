from .models import (
    Cup,
    CupTeams,
    CupDraw,
    Game,
    RankGroups,
    Winners,
    Medals,
    RankAllTime,
    CupCategory,
)
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django.contrib import admin

@admin.register(CupCategory)
class CupCategoryAdmin(ImportExportModelAdmin):
    list_display = ("name",)


@admin.action(description='Mark selected items as active')
def mark_as_active(modeladmin, request, queryset):
    queryset.update(c_active=True)

@admin.action(description='Mark selected items as inactive')
def mark_as_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.register(Cup)
class CupAdmin(ImportExportModelAdmin):
    list_display = (
        "c_name",
        "c_edition",
        "c_active",
        "category",
    )
    list_filter = (
        "c_active",
        "category",
    )
    ordering = ("c_name",)
    actions = [mark_as_active, mark_as_inactive]


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
